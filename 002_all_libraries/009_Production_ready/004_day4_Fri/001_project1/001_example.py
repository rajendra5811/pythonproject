import asyncio
import functools
import itertools
import json
import logging
import multiprocessing
import os
import re
import subprocess
import sys
import threading
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

import boto3
import httpx


class Student(TypedDict, total=False):
    id: int
    name: str
    city: str
    email: str
    marks: float
    grade: str
    source: str
    processed_at: str


class Config:
    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        api_url: str | None = None,
        s3_bucket: str | None = None,
        s3_key: str | None = None,
    ) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.api_url = api_url
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key


def configure_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


logger = logging.getLogger("student_elt")


# SOURCE: local JSON
def load_local_json(path: Path) -> list[dict[str, Any]]:
    logger.info("Reading local source: %s", path)
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Source JSON must contain a list of records.")

    return data


# SOURCE: remote HTTP API
async def load_remote_api(
    client: httpx.AsyncClient, url: str
) -> list[dict[str, Any]]:
    logger.info("Calling API source: %s", url)
    response = await client.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list):
        raise ValueError("API must return a JSON list.")
    return payload


async def extract_sources(config: Config) -> list[dict[str, Any]]:
    local_task = asyncio.to_thread(load_local_json, config.input_path)

    async with httpx.AsyncClient() as client:
        tasks = [local_task]
        if config.api_url:
            tasks.append(load_remote_api(client, config.api_url))
        results = await asyncio.gather(*tasks)

    combined: list[dict[str, Any]] = []
    for records in results:
        combined.extend(records)

    logger.info("Total extracted records: %d", len(combined))
    return combined


# TRANSFORM
def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name)).strip().title()


def normalize_city(city: str) -> str:
    return re.sub(r"[^A-Za-z ]", "", str(city)).strip().upper()


def normalize_email(email: str) -> str:
    return str(email).strip().lower()


def calculate_grade(marks: float) -> str:
    if marks >= 90:
        return "A"
    if marks >= 75:
        return "B"
    if marks >= 60:
        return "C"
    if marks >= 40:
        return "D"
    return "F"


@functools.lru_cache(maxsize=128)
def cached_grade(marks: float) -> str:
    return calculate_grade(marks)


def clean_record(record: dict[str, Any]) -> Student:
    marks = float(record.get("marks", 0))
    return Student(
        id=int(record["id"]),
        name=normalize_name(record.get("name", "Unknown")),
        city=normalize_city(record.get("city", "UNKNOWN")),
        email=normalize_email(record.get("email", "")),
        marks=marks,
        grade=cached_grade(marks),
        source=str(record.get("source", "unknown")),
        processed_at=datetime.now(timezone.utc).isoformat(),
    )


# CPU-oriented transformation
def transform_chunk(records: list[dict[str, Any]]) -> list[Student]:
    return [clean_record(record) for record in records]


def parallel_transform(records: list[dict[str, Any]]) -> list[Student]:
    if not records:
        return []

    workers = max(1, min(multiprocessing.cpu_count(), 4))
    chunk_size = max(1, (len(records) + workers - 1) // workers)
    chunks = [
        records[i:i + chunk_size]
        for i in range(0, len(records), chunk_size)
    ]

    with multiprocessing.Pool(processes=workers) as pool:
        transformed = pool.map(transform_chunk, chunks)

    return list(itertools.chain.from_iterable(transformed))


# VALIDATION
def validate_records(records: list[Student]) -> list[Student]:
    valid: list[Student] = []

    for record in records:
        if not record.get("id"):
            logger.warning("Dropping record without id")
            continue
        if not record.get("email"):
            logger.warning("Dropping record without email: %s", record["id"])
            continue
        if not 0 <= float(record["marks"]) <= 100:
            logger.warning("Dropping invalid marks: %s", record["id"])
            continue
        valid.append(record)

    return valid


def deduplicate(records: list[Student]) -> list[Student]:
    seen: set[int] = set()
    result: list[Student] = []

    for record in records:
        student_id = int(record["id"])
        if student_id not in seen:
            seen.add(student_id)
            result.append(record)

    return result


# AGGREGATION
def summarize(records: list[Student]) -> dict[str, Any]:
    city_counts = Counter(record["city"] for record in records)
    city_marks: defaultdict[str, list[float]] = defaultdict(list)

    for record in records:
        city_marks[record["city"]].append(float(record["marks"]))

    city_average = {
        city: round(sum(marks) / len(marks), 2)
        for city, marks in city_marks.items()
    }

    sorted_records = sorted(records, key=lambda x: x["grade"])
    grade_groups = {
        grade: list(group)
        for grade, group in itertools.groupby(
            sorted_records, key=lambda x: x["grade"]
        )
    }

    return {
        "record_count": len(records),
        "city_counts": dict(city_counts),
        "city_average_marks": city_average,
        "grade_counts": {
            grade: len(group) for grade, group in grade_groups.items()
        },
    }


# SINK: atomic local JSON
def write_json_atomic(
    records: list[Student],
    summary: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "record_count": len(records),
        },
        "summary": summary,
        "students": records,
    }

    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    temp_path.replace(output_path)
    logger.info("Wrote sink: %s", output_path)


# SINK: optional S3
def upload_to_s3(output_path: Path, bucket: str, key: str) -> None:
    s3 = boto3.client("s3")
    s3.upload_file(str(output_path), bucket, key)
    logger.info("Uploaded to s3://%s/%s", bucket, key)


# THREADING: blocking verification
def verify_output(output_path: Path) -> None:
    if not output_path.exists():
        raise FileNotFoundError(f"Output was not created: {output_path}")

    with output_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if "students" not in payload:
        raise ValueError("Output verification failed")

    logger.info("Verified output: %d records", len(payload["students"]))


def run_verification_thread(output_path: Path) -> None:
    thread = threading.Thread(
        target=verify_output,
        args=(output_path,),
        name="output-verifier",
    )
    thread.start()
    thread.join()


# SUBPROCESS + SYS
def runtime_check() -> None:
    result = subprocess.run(
        [sys.executable, "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    logger.info("Runtime: %s", result.stdout.strip())


def arg_value(flag: str, default: str | None = None) -> str | None:
    if flag not in sys.argv:
        return default
    index = sys.argv.index(flag)
    if index + 1 >= len(sys.argv):
        raise ValueError(f"Missing value for {flag}")
    return sys.argv[index + 1]


async def run_pipeline(config: Config) -> None:
    started = datetime.now(timezone.utc)
    logger.info("========== PIPELINE START ==========")

    runtime_check()

    raw = await extract_sources(config)
    transformed = parallel_transform(raw)
    validated = validate_records(transformed)
    unique = deduplicate(validated)
    summary = summarize(unique)

    write_json_atomic(unique, summary, config.output_path)
    run_verification_thread(config.output_path)

    if config.s3_bucket and config.s3_key:
        upload_to_s3(config.output_path, config.s3_bucket, config.s3_key)

    elapsed = datetime.now(timezone.utc) - started
    logger.info("Summary: %s", json.dumps(summary))
    logger.info("Elapsed: %s", elapsed)
    logger.info("========== PIPELINE SUCCESS ==========")


def main() -> None:
    configure_logging()

    config = Config(
        input_path=Path(arg_value("--input", "data/students.json")),
        output_path=Path(arg_value("--output", "output/students.json")),
        api_url=arg_value("--api-url"),
        s3_bucket=arg_value("--bucket"),
        s3_key=arg_value("--key"),
    )

    try:
        asyncio.run(run_pipeline(config))
    except Exception:
        logger.exception("PIPELINE FAILED")
        raise


if __name__ == "__main__":
    main()
import asyncio
import functools
import itertools
import json
import logging
import multiprocessing
import os
import re
import subprocess
import sys
import threading
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

import boto3
import httpx


class Student(TypedDict, total=False):
    id: int
    name: str
    city: str
    email: str
    marks: float
    grade: str
    source: str
    processed_at: str


class Config:
    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        api_url: str | None = None,
        s3_bucket: str | None = None,
        s3_key: str | None = None,
    ) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.api_url = api_url
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key


def configure_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


logger = logging.getLogger("student_elt")


# SOURCE: local JSON
def load_local_json(path: Path) -> list[dict[str, Any]]:
    logger.info("Reading local source: %s", path)
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Source JSON must contain a list of records.")

    return data


# SOURCE: remote HTTP API
async def load_remote_api(
    client: httpx.AsyncClient, url: str
) -> list[dict[str, Any]]:
    logger.info("Calling API source: %s", url)
    response = await client.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list):
        raise ValueError("API must return a JSON list.")
    return payload


async def extract_sources(config: Config) -> list[dict[str, Any]]:
    local_task = asyncio.to_thread(load_local_json, config.input_path)

    async with httpx.AsyncClient() as client:
        tasks = [local_task]
        if config.api_url:
            tasks.append(load_remote_api(client, config.api_url))
        results = await asyncio.gather(*tasks)

    combined: list[dict[str, Any]] = []
    for records in results:
        combined.extend(records)

    logger.info("Total extracted records: %d", len(combined))
    return combined


# TRANSFORM
def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name)).strip().title()


def normalize_city(city: str) -> str:
    return re.sub(r"[^A-Za-z ]", "", str(city)).strip().upper()


def normalize_email(email: str) -> str:
    return str(email).strip().lower()


def calculate_grade(marks: float) -> str:
    if marks >= 90:
        return "A"
    if marks >= 75:
        return "B"
    if marks >= 60:
        return "C"
    if marks >= 40:
        return "D"
    return "F"


@functools.lru_cache(maxsize=128)
def cached_grade(marks: float) -> str:
    return calculate_grade(marks)


def clean_record(record: dict[str, Any]) -> Student:
    marks = float(record.get("marks", 0))
    return Student(
        id=int(record["id"]),
        name=normalize_name(record.get("name", "Unknown")),
        city=normalize_city(record.get("city", "UNKNOWN")),
        email=normalize_email(record.get("email", "")),
        marks=marks,
        grade=cached_grade(marks),
        source=str(record.get("source", "unknown")),
        processed_at=datetime.now(timezone.utc).isoformat(),
    )


# CPU-oriented transformation
def transform_chunk(records: list[dict[str, Any]]) -> list[Student]:
    return [clean_record(record) for record in records]


def parallel_transform(records: list[dict[str, Any]]) -> list[Student]:
    if not records:
        return []

    workers = max(1, min(multiprocessing.cpu_count(), 4))
    chunk_size = max(1, (len(records) + workers - 1) // workers)
    chunks = [
        records[i:i + chunk_size]
        for i in range(0, len(records), chunk_size)
    ]

    with multiprocessing.Pool(processes=workers) as pool:
        transformed = pool.map(transform_chunk, chunks)

    return list(itertools.chain.from_iterable(transformed))


# VALIDATION
def validate_records(records: list[Student]) -> list[Student]:
    valid: list[Student] = []

    for record in records:
        if not record.get("id"):
            logger.warning("Dropping record without id")
            continue
        if not record.get("email"):
            logger.warning("Dropping record without email: %s", record["id"])
            continue
        if not 0 <= float(record["marks"]) <= 100:
            logger.warning("Dropping invalid marks: %s", record["id"])
            continue
        valid.append(record)

    return valid


def deduplicate(records: list[Student]) -> list[Student]:
    seen: set[int] = set()
    result: list[Student] = []

    for record in records:
        student_id = int(record["id"])
        if student_id not in seen:
            seen.add(student_id)
            result.append(record)

    return result


# AGGREGATION
def summarize(records: list[Student]) -> dict[str, Any]:
    city_counts = Counter(record["city"] for record in records)
    city_marks: defaultdict[str, list[float]] = defaultdict(list)

    for record in records:
        city_marks[record["city"]].append(float(record["marks"]))

    city_average = {
        city: round(sum(marks) / len(marks), 2)
        for city, marks in city_marks.items()
    }

    sorted_records = sorted(records, key=lambda x: x["grade"])
    grade_groups = {
        grade: list(group)
        for grade, group in itertools.groupby(
            sorted_records, key=lambda x: x["grade"]
        )
    }

    return {
        "record_count": len(records),
        "city_counts": dict(city_counts),
        "city_average_marks": city_average,
        "grade_counts": {
            grade: len(group) for grade, group in grade_groups.items()
        },
    }


# SINK: atomic local JSON
def write_json_atomic(
    records: list[Student],
    summary: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "record_count": len(records),
        },
        "summary": summary,
        "students": records,
    }

    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    temp_path.replace(output_path)
    logger.info("Wrote sink: %s", output_path)


# SINK: optional S3
def upload_to_s3(output_path: Path, bucket: str, key: str) -> None:
    s3 = boto3.client("s3")
    s3.upload_file(str(output_path), bucket, key)
    logger.info("Uploaded to s3://%s/%s", bucket, key)


# THREADING: blocking verification
def verify_output(output_path: Path) -> None:
    if not output_path.exists():
        raise FileNotFoundError(f"Output was not created: {output_path}")

    with output_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if "students" not in payload:
        raise ValueError("Output verification failed")

    logger.info("Verified output: %d records", len(payload["students"]))


def run_verification_thread(output_path: Path) -> None:
    thread = threading.Thread(
        target=verify_output,
        args=(output_path,),
        name="output-verifier",
    )
    thread.start()
    thread.join()


# SUBPROCESS + SYS
def runtime_check() -> None:
    result = subprocess.run(
        [sys.executable, "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    logger.info("Runtime: %s", result.stdout.strip())


def arg_value(flag: str, default: str | None = None) -> str | None:
    if flag not in sys.argv:
        return default
    index = sys.argv.index(flag)
    if index + 1 >= len(sys.argv):
        raise ValueError(f"Missing value for {flag}")
    return sys.argv[index + 1]


async def run_pipeline(config: Config) -> None:
    started = datetime.now(timezone.utc)
    logger.info("========== PIPELINE START ==========")

    runtime_check()

    raw = await extract_sources(config)
    transformed = parallel_transform(raw)
    validated = validate_records(transformed)
    unique = deduplicate(validated)
    summary = summarize(unique)

    write_json_atomic(unique, summary, config.output_path)
    run_verification_thread(config.output_path)

    if config.s3_bucket and config.s3_key:
        upload_to_s3(config.output_path, config.s3_bucket, config.s3_key)

    elapsed = datetime.now(timezone.utc) - started
    logger.info("Summary: %s", json.dumps(summary))
    logger.info("Elapsed: %s", elapsed)
    logger.info("========== PIPELINE SUCCESS ==========")


def main() -> None:
    configure_logging()

    config = Config(
        input_path=Path(arg_value("--input", "data/students.json")),
        output_path=Path(arg_value("--output", "output/students.json")),
        api_url=arg_value("--api-url"),
        s3_bucket=arg_value("--bucket"),
        s3_key=arg_value("--key"),
    )

    try:
        asyncio.run(run_pipeline(config))
    except Exception:
        logger.exception("PIPELINE FAILED")
        raise


if __name__ == "__main__":
    main()
