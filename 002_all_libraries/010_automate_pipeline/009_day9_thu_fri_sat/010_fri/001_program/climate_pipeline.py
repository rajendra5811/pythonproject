import asyncio
import json
import logging
import math
import os
import re
import sys

from collections import Counter, defaultdict
from datetime import datetime
from functools import reduce
from pathlib import Path
from typing import Any

import httpx
import boto3

from sqlalchemy import (
    create_engine,
    String,
    Float,
    Integer,
    DateTime,
    select
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_FILE = INPUT_DIR / "climate_readings.json"

CLEAN_FILE = OUTPUT_DIR / "clean_climate_data.json"
STATION_FILE = OUTPUT_DIR / "station_summary.json"
QUALITY_FILE = OUTPUT_DIR / "quality_report.json"

LOG_FILE = OUTPUT_DIR / "pipeline.log"

DATABASE_FILE = BASE_DIR / "climate.db"

AWS_BUCKET = "your-climate-bucket"

S3_OUTPUT_KEY = "climate/clean_climate_data.json"


# ============================================================
# DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# SQLALCHEMY DATABASE
# ============================================================

class Base(DeclarativeBase):
    pass


class ClimateReading(Base):

    __tablename__ = "climate_readings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    reading_id: Mapped[str] = mapped_column(
        String,
        unique=True
    )

    station_id: Mapped[str] = mapped_column(
        String
    )

    station_name: Mapped[str] = mapped_column(
        String
    )

    country: Mapped[str] = mapped_column(
        String
    )

    temperature_c: Mapped[float] = mapped_column(
        Float
    )

    humidity: Mapped[float] = mapped_column(
        Float
    )

    rainfall_mm: Mapped[float] = mapped_column(
        Float
    )

    wind_speed_kmh: Mapped[float] = mapped_column(
        Float
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime
    )


# ============================================================
# DATABASE SETUP
# ============================================================

engine = create_engine(
    f"sqlite:///{DATABASE_FILE}"
)

Base.metadata.create_all(engine)


# ============================================================
# VALIDATION
# ============================================================

def validate_reading(
    record: dict[str, Any]
) -> bool:

    required_fields = [
        "reading_id",
        "station_id",
        "station_name",
        "country",
        "temperature_c",
        "humidity",
        "rainfall_mm",
        "wind_speed_kmh",
        "recorded_at"
    ]

    for field in required_fields:

        if field not in record:
            return False

        if record[field] is None:
            return False

    # Temperature sanity check

    if not (
        -90 <= record["temperature_c"] <= 60
    ):
        return False

    # Humidity

    if not (
        0 <= record["humidity"] <= 100
    ):
        return False

    # Rainfall

    if record["rainfall_mm"] < 0:
        return False

    # Wind

    if record["wind_speed_kmh"] < 0:
        return False

    # Timestamp format

    pattern = (
        r"^\d{4}-\d{2}-\d{2} "
        r"\d{2}:\d{2}:\d{2}$"
    )

    if not re.match(
        pattern,
        record["recorded_at"]
    ):
        return False

    return True


# ============================================================
# TRANSFORMATION
# ============================================================

def transform_reading(
    record: dict[str, Any]
) -> dict[str, Any]:

    record["station_name"] = re.sub(
        r"\s+",
        " ",
        record["station_name"].strip()
    ).title()

    record["country"] = (
        record["country"]
        .strip()
        .upper()
    )

    timestamp = datetime.strptime(
        record["recorded_at"],
        "%Y-%m-%d %H:%M:%S"
    )

    record["recorded_at"] = (
        timestamp.isoformat()
    )

    # Heat index style learning metric
    record["temperature_f"] = round(
        (
            record["temperature_c"] * 9 / 5
        ) + 32,
        2
    )

    # Simple climate severity score

    record["climate_score"] = round(
        math.sqrt(
            record["humidity"] ** 2 +
            record["wind_speed_kmh"] ** 2
        ),
        2
    )

    return record


# ============================================================
# READ INPUT
# ============================================================

def read_input(
    file_path: Path
) -> list[dict[str, Any]]:

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# PROCESS RECORDS
# ============================================================

def process_records(
    records: list[dict[str, Any]]
) -> tuple[
    list[dict[str, Any]],
    int
]:

    clean_records = []

    rejected = 0

    for record in records:

        try:

            if not validate_reading(record):

                rejected += 1

                logger.warning(
                    "Rejected reading: %s",
                    record.get("reading_id")
                )

                continue

            clean_record = transform_reading(
                record
            )

            clean_records.append(
                clean_record
            )

        except Exception as error:

            rejected += 1

            logger.exception(
                "Record processing failed: %s",
                error
            )

    return (
        clean_records,
        rejected
    )


# ============================================================
# EXTERNAL COUNTRY API
# ============================================================

async def fetch_country(
    client: httpx.AsyncClient,
    country: str
) -> dict[str, Any]:

    url = (
        "https://restcountries.com/v3.1/alpha/"
        f"{country}"
    )

    try:

        response = await client.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()[0]

        return {
            "country_name":
                data.get(
                    "name",
                    {}
                ).get(
                    "common",
                    "Unknown"
                ),

            "region":
                data.get(
                    "region",
                    "Unknown"
                )
        }

    except Exception as error:

        logger.warning(
            "Country lookup failed for %s: %s",
            country,
            error
        )

        return {
            "country_name": "Unknown",
            "region": "Unknown"
        }


async def enrich_records(
    records: list[dict[str, Any]]
):

    countries = {
        record["country"]
        for record in records
    }

    async with httpx.AsyncClient() as client:

        tasks = [
            fetch_country(
                client,
                country
            )
            for country in countries
        ]

        results = await asyncio.gather(
            *tasks
        )

    lookup = dict(
        zip(
            countries,
            results
        )
    )

    for record in records:

        record.update(
            lookup[
                record["country"]
            ]
        )

    return records


# ============================================================
# STATION ANALYTICS
# ============================================================

def calculate_station_summary(
    records: list[dict[str, Any]]
):

    groups = defaultdict(list)

    for record in records:

        groups[
            record["station_id"]
        ].append(record)

    summary = {}

    for station_id, items in groups.items():

        temperatures = [
            item["temperature_c"]
            for item in items
        ]

        rainfall = [
            item["rainfall_mm"]
            for item in items
        ]

        total_rainfall = reduce(
            lambda x, y: x + y,
            rainfall,
            0
        )

        summary[station_id] = {

            "station_name":
                items[0]["station_name"],

            "country":
                items[0]["country"],

            "reading_count":
                len(items),

            "average_temperature_c":
                round(
                    sum(temperatures) /
                    len(temperatures),
                    2
                ),

            "maximum_temperature_c":
                max(temperatures),

            "minimum_temperature_c":
                min(temperatures),

            "total_rainfall_mm":
                round(
                    total_rainfall,
                    2
                )
        }

    return summary


# ============================================================
# DATABASE INSERT
# ============================================================

def save_to_database(
    records: list[dict[str, Any]]
):

    with Session(engine) as session:

        for record in records:

            reading = ClimateReading(

                reading_id=
                    record["reading_id"],

                station_id=
                    record["station_id"],

                station_name=
                    record["station_name"],

                country=
                    record["country"],

                temperature_c=
                    record["temperature_c"],

                humidity=
                    record["humidity"],

                rainfall_mm=
                    record["rainfall_mm"],

                wind_speed_kmh=
                    record["wind_speed_kmh"],

                recorded_at=
                    datetime.fromisoformat(
                        record["recorded_at"]
                    )
            )

            session.add(reading)

        session.commit()

    logger.info(
        "Saved %s records to database",
        len(records)
    )


# ============================================================
# DATABASE QUERY
# ============================================================

def count_database_records():

    with Session(engine) as session:

        statement = select(
            ClimateReading
        )

        records = session.scalars(
            statement
        ).all()

        return len(records)


# ============================================================
# AWS S3 SINK
# ============================================================

def upload_to_s3(
    file_path: Path
):

    try:

        s3 = boto3.client("s3")

        s3.upload_file(
            str(file_path),
            AWS_BUCKET,
            S3_OUTPUT_KEY
        )

        logger.info(
            "Uploaded %s to S3",
            file_path
        )

    except Exception as error:

        logger.exception(
            "S3 upload failed: %s",
            error
        )


# ============================================================
# WRITE JSON
# ============================================================

def write_json(
    data: Any,
    file_path: Path
):

    with file_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline():

    logger.info(
        "CLIMATE RESEARCH PIPELINE STARTED"
    )

    logger.info(
        "OS: %s",
        os.name
    )

    logger.info(
        "Python: %s",
        sys.version
    )

    try:

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        records = read_input(
            INPUT_FILE
        )

        total_input = len(records)

        # ----------------------------------------------------
        # VALIDATION + TRANSFORMATION
        # ----------------------------------------------------

        clean_records, rejected = (
            process_records(records)
        )

        # ----------------------------------------------------
        # API ENRICHMENT
        # ----------------------------------------------------

        clean_records = asyncio.run(
            enrich_records(
                clean_records
            )
        )

        # ----------------------------------------------------
        # ANALYTICS
        # ----------------------------------------------------

        station_summary = (
            calculate_station_summary(
                clean_records
            )
        )

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        save_to_database(
            clean_records
        )

        database_count = (
            count_database_records()
        )

        # ----------------------------------------------------
        # QUALITY
        # ----------------------------------------------------

        rejection_rate = 0

        if total_input:

            rejection_rate = (
                rejected /
                total_input
            ) * 100

        quality_report = {

            "total_input":
                total_input,

            "clean_records":
                len(clean_records),

            "rejected_records":
                rejected,

            "rejection_rate":
                round(
                    rejection_rate,
                    2
                ),

            "database_records":
                database_count
        }

        # ----------------------------------------------------
        # LOCAL SINK
        # ----------------------------------------------------

        write_json(
            clean_records,
            CLEAN_FILE
        )

        write_json(
            station_summary,
            STATION_FILE
        )

        write_json(
            quality_report,
            QUALITY_FILE
        )

        # ----------------------------------------------------
        # CLOUD SINK
        # ----------------------------------------------------

        upload_to_s3(
            CLEAN_FILE
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        logger.info(
            "Input records: %s",
            total_input
        )

        logger.info(
            "Clean records: %s",
            len(clean_records)
        )

        logger.info(
            "Rejected records: %s",
            rejected
        )

        logger.info(
            "CLIMATE RESEARCH PIPELINE "
            "COMPLETED SUCCESSFULLY"
        )

    except Exception as error:

        logger.exception(
            "CLIMATE PIPELINE FAILED: %s",
            error
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_pipeline()