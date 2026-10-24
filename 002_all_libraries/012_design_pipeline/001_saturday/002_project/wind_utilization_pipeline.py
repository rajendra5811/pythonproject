# ============================================================
# WIND UTILIZATION PIPELINE
# PHASE 1 - COPY PROGRAM
# ============================================================

import os
import sys
import json
import math
import re
import logging
import asyncio
import subprocess

from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from functools import lru_cache
from itertools import groupby
from typing import List, Dict, Any

import httpx
import boto3

from multiprocessing import Pool
from threading import Thread

from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///wind.db"
)

S3_BUCKET = os.getenv(
    "WIND_S3_BUCKET",
    ""
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# 2. DATABASE MODEL
# ============================================================

Base = declarative_base()


class WindReport(Base):

    __tablename__ = "wind_reports"

    turbine_id = Column(
        String,
        primary_key=True
    )

    farm = Column(String)

    utilization = Column(Float)

    average_wind_speed = Column(Float)

    generated_kwh = Column(Float)

    processed_at = Column(DateTime)


engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


# ============================================================
# 3. FILE DISCOVERY
# pathlib
# ============================================================

def discover_files() -> List[Path]:

    return list(
        INPUT_DIR.glob("*.json")
    )


# ============================================================
# 4. JSON READING
# json
# ============================================================

def read_file(path: Path) -> List[Dict[str, Any]]:

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# 5. VALIDATION
# re + datetime + math
# ============================================================

def validate(record: Dict[str, Any]) -> bool:

    turbine_id = record.get("turbine_id")

    if not re.fullmatch(
        r"WT\d{3}",
        turbine_id or ""
    ):
        return False

    try:

        datetime.fromisoformat(
            record["timestamp"]
        )

    except (ValueError, TypeError):

        return False

    wind_speed = record.get("wind_speed")

    generated = record.get("generated_kwh")

    capacity = record.get("capacity_kw")

    if not isinstance(wind_speed, (int, float)):
        return False

    if not isinstance(generated, (int, float)):
        return False

    if not isinstance(capacity, (int, float)):
        return False

    if wind_speed < 0:
        return False

    if generated < 0:
        return False

    if capacity <= 0:
        return False

    if not math.isfinite(wind_speed):
        return False

    return True


# ============================================================
# 6. TRANSFORMATION
# ============================================================

def transform(record):

    record["farm"] = (
        " ".join(
            record["farm"]
            .strip()
            .upper()
            .split()
        )
    )

    record["timestamp"] = datetime.fromisoformat(
        record["timestamp"]
    )

    return record


# ============================================================
# 7. CACHED BUSINESS RULE
# functools
# ============================================================

@lru_cache(maxsize=10)
def utilization_category(utilization):

    if utilization >= 80:
        return "excellent"

    if utilization >= 50:
        return "good"

    return "low"


# ============================================================
# 8. PROCESS ONE FILE
# ============================================================

def process_file(path):

    logger.info(
        "Processing %s",
        path.name
    )

    records = read_file(path)

    valid_records = []

    for record in records:

        if not validate(record):

            logger.warning(
                "Rejected record: %s",
                record.get("turbine_id")
            )

            continue

        valid_records.append(
            transform(record)
        )

    return valid_records


# ============================================================
# 9. MULTIPROCESSING
# multiprocessing
# ============================================================

def process_files_parallel(files):

    with Pool() as pool:

        results = pool.map(
            process_file,
            files
        )

    records = []

    for batch in results:

        records.extend(batch)

    return records


# ============================================================
# 10. AGGREGATION
# defaultdict + Counter
# ============================================================

def aggregate(records):

    grouped = defaultdict(
        lambda: {
            "farm": "",
            "generated": 0,
            "capacity": 0,
            "wind_speeds": []
        }
    )

    status_counter = Counter()

    for record in records:

        turbine = record["turbine_id"]

        grouped[turbine]["farm"] = (
            record["farm"]
        )

        grouped[turbine]["generated"] += (
            record["generated_kwh"]
        )

        grouped[turbine]["capacity"] += (
            record["capacity_kw"]
        )

        grouped[turbine]["wind_speeds"].append(
            record["wind_speed"]
        )

        status_counter[
            record["status"]
        ] += 1

    return grouped, status_counter


# ============================================================
# 11. GROUPING
# itertools
# ============================================================

def farm_groups(records):

    records = sorted(
        records,
        key=lambda x: x["farm"]
    )

    result = {}

    for farm, group in groupby(
        records,
        key=lambda x: x["farm"]
    ):

        result[farm] = list(group)

    return result


# ============================================================
# 12. BUSINESS TRANSFORMATION
# math
# ============================================================

def create_report(grouped):

    report = {}

    for turbine, data in grouped.items():

        utilization = (
            data["generated"]
            / data["capacity"]
        ) * 100

        average_wind = (
            sum(data["wind_speeds"])
            / len(data["wind_speeds"])
        )

        utilization = math.floor(
            utilization * 100
        ) / 100

        report[turbine] = {

            "farm": data["farm"],

            "generated_kwh":
                data["generated"],

            "utilization_percent":
                utilization,

            "utilization_category":
                utilization_category(
                    utilization
                ),

            "average_wind_speed":
                round(
                    average_wind,
                    2
                ),

            "processed_at":
                datetime.now().isoformat()
        }

    return report


# ============================================================
# 13. DATABASE SINK
# SQLAlchemy
# ============================================================

def save_database(report):

    session = Session()

    try:

        for turbine_id, data in report.items():

            row = WindReport(
                turbine_id=turbine_id,
                farm=data["farm"],
                utilization=data[
                    "utilization_percent"
                ],
                average_wind_speed=data[
                    "average_wind_speed"
                ],
                generated_kwh=data[
                    "generated_kwh"
                ],
                processed_at=datetime.fromisoformat(
                    data["processed_at"]
                )
            )

            session.merge(row)

        session.commit()

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()


# ============================================================
# 14. JSON SINK
# ============================================================

def write_json(report):

    output_file = (
        OUTPUT_DIR /
        "wind_utilization.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    return output_file


# ============================================================
# 15. ASYNC WEATHER ENRICHMENT
# httpx + asyncio
# ============================================================

async def get_weather(client, farm):

    try:

        response = await client.get(
            "https://example.com/weather",
            params={"farm": farm},
            timeout=5
        )

        return {
            "farm": farm,
            "weather_status":
                response.status_code
        }

    except httpx.HTTPError:

        return {
            "farm": farm,
            "weather_status": "unavailable"
        }


async def enrich_weather(farms):

    async with httpx.AsyncClient() as client:

        tasks = [
            get_weather(client, farm)
            for farm in farms
        ]

        return await asyncio.gather(
            *tasks
        )

#S3 SINK( boto3)

def upload_s3(output_file):

    if not S3_BUCKET:

        logger.info(
            "S3 bucket not configured"
        )

        return

    s3 = boto3.client("s3")

    s3.upload_file(
        str(output_file),
        S3_BUCKET,
        "wind/wind_utilization.json"
    )

    logger.info(
        "Uploaded report to S3"
    )
#SYSTEM INFORMATION(subprocess)
def system_info():

    try:

        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True
        )

        return result.stdout.strip()

    except Exception:

        return "unknown"
#BACKGROUND MONITORING(threading)
def monitor():

    logger.info(
        "Background monitor: pipeline alive"
    )


def start_monitor():

    thread = Thread(
        target=monitor,
        daemon=True
    )

    thread.start()

#PIPELINE
def run_pipeline():

    logger.info(
        "Wind pipeline started"
    )

    start_monitor()

    logger.info(
        "Runtime: %s",
        system_info()
    )

    files = discover_files()

    if not files:

        logger.error(
            "No input files found"
        )

        sys.exit(1)

    # SOURCE
    records = process_files_parallel(
        files
    )

    # TRANSFORMATION
    grouped, status_counter = aggregate(
        records
    )

    # BUSINESS LOGIC
    report = create_report(
        grouped
    )

    # DATABASE SINK
    save_database(report)

    # JSON SINK
    output_file = write_json(
        report
    )

    # CLOUD SINK
    upload_s3(output_file)

    logger.info(
        "Records processed: %d",
        len(records)
    )

    logger.info(
        "Status summary: %s",
        dict(status_counter)
    )

    logger.info(
        "Wind pipeline completed"
    )
# main
if __name__ == "__main__":

    try:

        run_pipeline()

    except Exception as error:

        logger.exception(
            "Pipeline failed: %s",
            error
        )

        sys.exit(1)