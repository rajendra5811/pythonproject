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
from functools import reduce
from itertools import groupby
from multiprocessing import Pool
from typing import List, Dict, Any

import httpx
import boto3

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. CONFIGURATION


BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)



# 2. DATABASE MODEL


Base = declarative_base()


class SolarUsage(Base):

    __tablename__ = "solar_usage"

    id = Column(Integer, primary_key=True)
    plant_id = Column(String)
    city = Column(String)
    generated_kwh = Column(Float)
    consumed_kwh = Column(Float)
    utilization = Column(Float)


engine = create_engine("sqlite:///solar.db")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


# 3. FILE DISCOVERY


def discover_files() -> List[Path]:

    logger.info("Discovering solar JSON files")

    return list(INPUT_DIR.glob("*.json"))


# 4. READ JSON


def read_json(file_path: Path) -> List[Dict[str, Any]]:

    logger.info("Reading %s", file_path.name)

    with file_path.open("r", encoding="utf-8") as file:

        return json.load(file)


# 5. CLEAN CITY


def clean_city(city: str) -> str:

    city = city.strip().upper()

    city = re.sub(r"\s+", " ", city)

    return city



# 6. VALIDATE RECORD


def validate_record(record: Dict[str, Any]) -> bool:

    required_fields = [
        "plant_id",
        "city",
        "timestamp",
        "generated_kwh",
        "consumed_kwh",
        "battery_kwh",
        "temperature"
    ]

    for field in required_fields:

        if field not in record:

            logger.warning(
                "Missing field: %s",
                field
            )

            return False

    if record["generated_kwh"] < 0:

        logger.warning("Negative generation rejected")

        return False

    if record["consumed_kwh"] < 0:

        logger.warning("Negative consumption rejected")

        return False

    return True


# 7. TRANSFORM RECORD


def transform_record(record: Dict[str, Any]) -> Dict[str, Any]:

    generated = record["generated_kwh"]
    consumed = record["consumed_kwh"]

    utilization = 0

    if generated > 0:

        utilization = (
            consumed / generated
        ) * 100

    return {

        "plant_id":
            record["plant_id"].strip(),

        "city":
            clean_city(record["city"]),

        "timestamp":
            datetime.strptime(
                record["timestamp"],
                "%Y-%m-%d %H:%M:%S"
            ).isoformat(),

        "generated_kwh":
            generated,

        "consumed_kwh":
            consumed,

        "battery_kwh":
            record["battery_kwh"],

        "temperature":
            record["temperature"],

        "utilization":
            round(utilization, 2)
    }



# 8. PROCESS RECORDS


def process_records(
    records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    processed = []

    for record in records:

        if not validate_record(record):

            continue

        try:

            transformed = transform_record(record)

            processed.append(transformed)

        except Exception as error:

            logger.error(
                "Transformation failed: %s",
                error
            )

    return processed


# 9. AGGREGATE BY PLANT


def aggregate_by_plant(
    records: List[Dict[str, Any]]
) -> Dict[str, Any]:

    totals = defaultdict(
        lambda: {
            "generated_kwh": 0,
            "consumed_kwh": 0,
            "records": 0
        }
    )

    for record in records:

        plant = record["plant_id"]

        totals[plant]["generated_kwh"] += (
            record["generated_kwh"]
        )

        totals[plant]["consumed_kwh"] += (
            record["consumed_kwh"]
        )

        totals[plant]["records"] += 1

    return dict(totals)

# 10. AGGREGATE BY CITY


def aggregate_by_city(
    records: List[Dict[str, Any]]
) -> Dict[str, Any]:

    city_counter = Counter()

    city_generation = defaultdict(float)

    for record in records:

        city = record["city"]

        city_counter[city] += 1

        city_generation[city] += (
            record["generated_kwh"]
        )

    return {

        "record_count":
            dict(city_counter),

        "generation_kwh":
            dict(city_generation)
    }

# 11. MATHEMATICAL METRICS


def calculate_metrics(
    records: List[Dict[str, Any]]
) -> Dict[str, float]:

    generated = sum(
        record["generated_kwh"]
        for record in records
    )

    consumed = sum(
        record["consumed_kwh"]
        for record in records
    )

    utilization = 0

    if generated > 0:

        utilization = (
            consumed / generated
        ) * 100

    return {

        "total_generated_kwh":
            round(generated, 2),

        "total_consumed_kwh":
            round(consumed, 2),

        "utilization_percent":
            round(utilization, 2)
    }


# 12. WRITE JSON


def write_json(
    data: Any,
    filename: str
):

    output_file = OUTPUT_DIR / filename

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

    logger.info(
        "Output written: %s",
        output_file
    )



# 13. DATABASE LOAD


def load_database(
    records: List[Dict[str, Any]]
):

    session = Session()

    try:

        for record in records:

            row = SolarUsage(

                plant_id=record["plant_id"],

                city=record["city"],

                generated_kwh=
                    record["generated_kwh"],

                consumed_kwh=
                    record["consumed_kwh"],

                utilization=
                    record["utilization"]
            )

            session.add(row)

        session.commit()

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()

# 14. ASYNC WEATHER CALL


async def fetch_weather():

    url = "https://api.open-meteo.com/v1/forecast"

    params = {

        "latitude": 17.3850,

        "longitude": 78.4867,

        "current":
            "temperature_2m"
    }

    async with httpx.AsyncClient() as client:

        try:

            response = await client.get(
                url,
                params=params,
                timeout=10
            )

            return response.json()

        except Exception as error:

            logger.warning(
                "Weather API failed: %s",
                error
            )

            return {}


def get_weather():

    return asyncio.run(
        fetch_weather()
    )

# 15. THREADING EXAMPLE


def background_task():

    logger.info(
        "Background monitoring started"
    )


def start_monitoring():

    thread = threading.Thread(
        target=background_task
    )

    thread.start()

    thread.join()

# 16. SYSTEM INFORMATION


def system_info():

    logger.info(
        "Python version: %s",
        sys.version
    )

    logger.info(
        "Working directory: %s",
        os.getcwd()
    )


# 17. SUBPROCESS


def check_system():

    try:

        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True
        )

        logger.info(
            "Runtime: %s",
            result.stdout.strip()
            or result.stderr.strip()
        )

    except Exception as error:

        logger.warning(
            "System check failed: %s",
            error
        )


# 18. FUNCTOOLS + ITERTOOLS


def calculate_total(
    records: List[Dict[str, Any]]
):

    values = [
        record["generated_kwh"]
        for record in records
    ]

    return reduce(
        lambda x, y: x + y,
        values,
        0
    )


def group_records(
    records: List[Dict[str, Any]]
):

    sorted_records = sorted(
        records,
        key=lambda x: x["city"]
    )

    return {

        city: list(group)

        for city, group in groupby(
            sorted_records,
            key=lambda x: x["city"]
        )
    }

# 19. S3 SINK


def upload_to_s3(
    filename: str
):

    try:

        s3 = boto3.client("s3")

        bucket = os.getenv(
            "SOLAR_BUCKET"
        )

        if not bucket:

            logger.warning(
                "SOLAR_BUCKET not configured"
            )

            return

        file_path = OUTPUT_DIR / filename

        s3.upload_file(
            str(file_path),
            bucket,
            filename
        )

        logger.info(
            "Uploaded %s to S3",
            filename
        )

    except Exception as error:

        logger.warning(
            "S3 upload failed: %s",
            error
        )


# 20. MAIN PIPELINE

def run_pipeline():

    logger.info(
        "========== SOLAR PIPELINE START =========="
    )

    system_info()

    check_system()

    start_monitoring()

    files = discover_files()

    all_records = []

    for file_path in files:

        records = read_json(
            file_path
        )

        processed = process_records(
            records
        )

        all_records.extend(
            processed
        )

    plant_summary = aggregate_by_plant(
        all_records
    )

    city_summary = aggregate_by_city(
        all_records
    )

    metrics = calculate_metrics(
        all_records
    )

    total = calculate_total(
        all_records
    )

    groups = group_records(
        all_records
    )

    weather = get_weather()

    output = {

        "metrics": metrics,

        "plant_summary":
            plant_summary,

        "city_summary":
            city_summary,

        "generated_total":
            total,

        "city_groups":
            groups,

        "weather":
            weather
    }

    write_json(
        output,
        "solar_report.json"
    )

    load_database(
        all_records
    )

    upload_to_s3(
        "solar_report.json"
    )

    logger.info(
        "========== SOLAR PIPELINE COMPLETE =========="
    )


##main entry point
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