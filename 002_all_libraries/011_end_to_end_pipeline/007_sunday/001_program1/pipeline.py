import os
import sys
import json
import math
import re
import logging
import asyncio
import threading
import subprocess

from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from functools import lru_cache
from itertools import groupby
from multiprocessing import Pool
from typing import List, Dict, Any

import httpx

import boto3

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float
)

from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///attendance.db"
)

S3_BUCKET = os.getenv(
    "ATTENDANCE_BUCKET"
)

HOLIDAY_API = os.getenv(
    "HOLIDAY_API",
    "https://date.nager.at/api/v3/PublicHolidays"
)


# ============================================================
# 2. LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("attendance_pipeline")


# ============================================================
# 3. DATABASE
# ============================================================

Base = declarative_base()


class Attendance(Base):

    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True
    )

    student_id = Column(
        String,
        nullable=False
    )

    student_name = Column(
        String,
        nullable=False
    )

    class_name = Column(
        String,
        nullable=False
    )

    attendance_date = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )


class AttendanceSummary(Base):

    __tablename__ = "attendance_summary"

    id = Column(
        Integer,
        primary_key=True
    )

    student_id = Column(String)

    attendance_percent = Column(Float)


engine = create_engine(
    DATABASE_URL
)

Base.metadata.create_all(engine)

Session = sessionmaker(
    bind=engine
)


# ============================================================
# 4. FILE DISCOVERY
# ============================================================

def discover_files() -> List[Path]:

    files = list(
        INPUT_DIR.glob("*.json")
    )

    logger.info(
        "Discovered %d files",
        len(files)
    )

    return files


# ============================================================
# 5. JSON READING
# ============================================================

def read_json(
    path: Path
) -> List[Dict[str, Any]]:

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# 6. PARALLEL FILE READING
# multiprocessing
# ============================================================

def read_file_worker(
    path: Path
) -> List[Dict[str, Any]]:

    return read_json(path)


def read_all_files(
    files: List[Path]
) -> List[Dict[str, Any]]:

    with Pool() as pool:

        results = pool.map(
            read_file_worker,
            files
        )

    records = []

    for result in results:

        records.extend(result)

    return records


# ============================================================
# 7. STUDENT ID VALIDATION
# re
# ============================================================

def valid_student_id(
    student_id: str
) -> bool:

    return bool(
        re.fullmatch(
            r"STU\d{3,}",
            student_id
        )
    )


# ============================================================
# 8. RECORD VALIDATION
# ============================================================

def validate_record(
    record: Dict[str, Any]
) -> bool:

    required = [
        "student_id",
        "student_name",
        "class_name",
        "date",
        "status"
    ]

    if not all(
        field in record
        for field in required
    ):
        return False

    if not valid_student_id(
        record["student_id"]
    ):
        return False

    if record["status"] not in {
        "present",
        "absent",
        "late"
    }:
        return False

    try:

        datetime.strptime(
            record["date"],
            "%Y-%m-%d"
        )

    except ValueError:

        return False

    return True


# ============================================================
# 9. PARALLEL VALIDATION
# multiprocessing
# ============================================================

def validate_records(
    records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    with Pool() as pool:

        valid = pool.map(
            validate_record,
            records
        )

    clean_records = [
        record
        for record, is_valid
        in zip(records, valid)
        if is_valid
    ]

    logger.info(
        "Valid records: %d / %d",
        len(clean_records),
        len(records)
    )

    return clean_records


# ============================================================
# 10. TRANSFORMATION
# ============================================================

def transform(
    record: Dict[str, Any]
) -> Dict[str, Any]:

    return {

        "student_id":
            record["student_id"].strip(),

        "student_name":
            " ".join(
                record["student_name"]
                .strip()
                .split()
            ),

        "class_name":
            record["class_name"]
            .strip()
            .upper(),

        "date":
            datetime.strptime(
                record["date"],
                "%Y-%m-%d"
            ).date(),

        "status":
            record["status"]
            .strip()
            .lower()
    }


# ============================================================
# 11. ATTENDANCE VALUE
# ============================================================

def attendance_value(
    status: str
) -> float:

    if status == "present":

        return 1.0

    if status == "late":

        return 0.5

    return 0.0


# ============================================================
# 12. MATH
# ============================================================

def percentage(
    attended: int,
    total: int
) -> float:

    if total == 0:

        return 0.0

    value = (
        attended / total
    ) * 100

    return math.floor(
        value * 100
    ) / 100


# ============================================================
# 13. CACHED POLICY
# functools
# ============================================================

@lru_cache(maxsize=10)
def minimum_attendance(
    class_name: str
) -> float:

    # School policy example

    if class_name.startswith("10"):

        return 75.0

    return 70.0


# ============================================================
# 14. STUDENT AGGREGATION
# collections
# ============================================================

def student_summary(
    records: List[Dict[str, Any]]
):

    stats = defaultdict(
        lambda: {
            "attended": 0,
            "total": 0
        }
    )

    for record in records:

        student = record["student_id"]

        stats[student]["total"] += 1

        stats[student]["attended"] += (
            attendance_value(
                record["status"]
            )
        )

    result = {}

    for student, data in stats.items():

        result[student] = {

            "attended":
                data["attended"],

            "total":
                data["total"],

            "percentage":
                percentage(
                    data["attended"],
                    data["total"]
                )
        }

    return result


# ============================================================
# 15. CLASS COUNTER
# collections.Counter
# ============================================================

def class_status_summary(
    records
):

    result = defaultdict(Counter)

    for record in records:

        result[
            record["class_name"]
        ][record["status"]] += 1

    return {
        key: dict(value)
        for key, value
        in result.items()
    }


# ============================================================
# 16. ITERTOOLS GROUPING
# ============================================================

def group_by_class(
    records
):

    ordered = sorted(
        records,
        key=lambda x: x["class_name"]
    )

    groups = {}

    for class_name, group in groupby(
        ordered,
        key=lambda x: x["class_name"]
    ):

        groups[class_name] = list(group)

    return groups


# ============================================================
# 17. ASYNC HOLIDAY API
# httpx + asyncio
# ============================================================

async def fetch_holidays(
    year: int
):

    url = (
        f"{HOLIDAY_API}/"
        f"{year}/IN"
    )

    async with httpx.AsyncClient(
        timeout=10
    ) as client:

        try:

            response = await client.get(
                url
            )

            response.raise_for_status()

            return response.json()

        except Exception as error:

            logger.warning(
                "Holiday API failed: %s",
                error
            )

            return []


def get_holidays(
    year: int
):

    return asyncio.run(
        fetch_holidays(year)
    )


# ============================================================
# 18. DATABASE LOAD
# SQLAlchemy
# ============================================================

def load_database(
    records,
    summaries
):

    session = Session()

    try:

        for record in records:

            row = Attendance(

                student_id=
                    record["student_id"],

                student_name=
                    record["student_name"],

                class_name=
                    record["class_name"],

                attendance_date=
                    str(record["date"]),

                status=
                    record["status"]
            )

            session.add(row)

        for student, data in summaries.items():

            row = AttendanceSummary(

                student_id=student,

                attendance_percent=
                    data["percentage"]
            )

            session.add(row)

        session.commit()

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()


# ============================================================
# 19. JSON SINK
# ============================================================

def write_report(
    report
):

    path = (
        OUTPUT_DIR /
        "attendance_report.json"
    )

    with path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str
        )

    return path


# ============================================================
# 20. S3 SINK
# boto3
# ============================================================

def upload_s3(
    path: Path
):

    if not S3_BUCKET:

        logger.info(
            "S3 bucket not configured"
        )

        return

    client = boto3.client(
        "s3"
    )

    client.upload_file(
        str(path),
        S3_BUCKET,
        path.name
    )

    logger.info(
        "Report uploaded to S3"
    )


# ============================================================
# 21. THREADING
# ============================================================

def background_monitor():

    logger.info(
        "Monitoring thread started"
    )


def start_monitoring():

    thread = threading.Thread(
        target=background_monitor
    )

    thread.start()

    return thread


# ============================================================
# 22. SUBPROCESS
# ============================================================

def get_git_version():

    try:

        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "--short",
                "HEAD"
            ],
            capture_output=True,
            text=True,
            check=False
        )

        return result.stdout.strip()

    except Exception:

        return "unknown"


# ============================================================
# 23. MAIN PIPELINE
# ============================================================

def run_pipeline():

    logger.info(
        "===== ATTENDANCE PIPELINE START ====="
    )

    logger.info(
        "Pipeline version: %s",
        get_git_version()
    )

    monitor = start_monitoring()

    files = discover_files()

    if not files:

        logger.warning(
            "No attendance files found"
        )

        return

    raw_records = read_all_files(
        files
    )

    valid_records = validate_records(
        raw_records
    )

    records = [
        transform(record)
        for record in valid_records
    ]

    summaries = student_summary(
        records
    )

    class_summary = class_status_summary(
        records
    )

    class_groups = group_by_class(
        records
    )

    years = {
        record["date"].year
        for record in records
    }

    holidays = []

    for year in years:

        holidays.extend(
            get_holidays(year)
        )

    report = {

        "pipeline_version":
            get_git_version(),

        "processed_records":
            len(records),

        "students":
            summaries,

        "classes":
            class_summary,

        "groups":
            {
                key: len(value)
                for key, value
                in class_groups.items()
            },

        "minimum_policy":
            {
                key:
                    minimum_attendance(key)
                for key in class_groups
            },

        "holidays":
            holidays
    }

    report_path = write_report(
        report
    )

    load_database(
        records,
        summaries
    )

    upload_s3(
        report_path
    )

    monitor.join()

    logger.info(
        "===== ATTENDANCE PIPELINE COMPLETE ====="
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        run_pipeline()

    except KeyboardInterrupt:

        logger.warning(
            "Pipeline interrupted"
        )

        sys.exit(1)

    except Exception as error:

        logger.exception(
            "Pipeline failed: %s",
            error
        )

        sys.exit(1)