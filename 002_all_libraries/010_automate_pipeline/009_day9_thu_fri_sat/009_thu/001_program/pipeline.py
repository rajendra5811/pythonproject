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


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

SOURCE_DIR = BASE_DIR / "content_data"
OUTPUT_DIR = BASE_DIR / "output"

CLEAN_FILE = OUTPUT_DIR / "clean_content.json"
CATEGORY_FILE = OUTPUT_DIR / "category_summary.json"
CREATOR_FILE = OUTPUT_DIR / "creator_summary.json"
QUALITY_FILE = OUTPUT_DIR / "quality_report.json"
PIPELINE_LOG = OUTPUT_DIR / "pipeline.log"


# ============================================================
# LOGGING
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=PIPELINE_LOG,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# VALIDATION
# ============================================================

def validate_content(record: dict[str, Any]) -> bool:

    required_fields = [
        "video_id",
        "title",
        "creator",
        "category",
        "views",
        "duration_minutes",
        "published_at",
        "country"
    ]

    for field in required_fields:

        if field not in record:
            return False

        if record[field] is None:
            return False

    if not isinstance(record["views"], (int, float)):
        return False

    if record["views"] < 0:
        return False

    if record["duration_minutes"] <= 0:
        return False

    timestamp_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"

    if not re.match(timestamp_pattern, record["published_at"]):
        return False

    valid_categories = {
        "technology",
        "education",
        "entertainment",
        "sports"
    }

    if record["category"].lower() not in valid_categories:
        return False

    return True


# ============================================================
# TRANSFORMATION
# ============================================================

def transform_content(record: dict[str, Any]) -> dict[str, Any]:

    record["creator"] = re.sub(
        r"\s+",
        " ",
        record["creator"].strip()
    ).title()

    record["title"] = record["title"].strip()

    record["category"] = record["category"].strip().lower()

    record["country"] = record["country"].strip().upper()

    published_time = datetime.strptime(
        record["published_at"],
        "%Y-%m-%d %H:%M:%S"
    )

    record["published_at"] = published_time.isoformat()

    record["engagement_score"] = round(
        math.log1p(record["views"]) *
        record["duration_minutes"],
        2
    )

    return record


# ============================================================
# FILE DISCOVERY
# ============================================================

def discover_files(source_dir: Path) -> list[Path]:

    files = list(source_dir.glob("*.json"))

    logger.info(
        "Discovered %s content files",
        len(files)
    )

    return files


# ============================================================
# JSON READER
# ============================================================

def read_json(file_path: Path) -> list[dict[str, Any]]:

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# PROCESS FILES
# ============================================================

def process_files(
    files: list[Path]
) -> tuple[list[dict[str, Any]], int]:

    clean_records = []
    rejected_records = 0

    for file_path in files:

        try:

            records = read_json(file_path)

            for record in records:

                if not validate_content(record):

                    rejected_records += 1

                    logger.warning(
                        "Rejected record from %s",
                        file_path.name
                    )

                    continue

                transformed = transform_content(record)

                clean_records.append(transformed)

        except Exception as error:

            logger.exception(
                "Failed processing file %s: %s",
                file_path.name,
                error
            )

    return clean_records, rejected_records


# ============================================================
# EXTERNAL API ENRICHMENT
# ============================================================

async def fetch_country_data(
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

        data = response.json()

        country_data = data[0]

        return {
            "country_name":
                country_data.get("name", {}).get(
                    "common",
                    "Unknown"
                ),
            "region":
                country_data.get(
                    "region",
                    "Unknown"
                )
        }

    except Exception as error:

        logger.warning(
            "Country API failed for %s: %s",
            country,
            error
        )

        return {
            "country_name": "Unknown",
            "region": "Unknown"
        }


async def enrich_records(
    records: list[dict[str, Any]]
) -> list[dict[str, Any]]:

    countries = {
        record["country"]
        for record in records
    }

    async with httpx.AsyncClient() as client:

        tasks = [
            fetch_country_data(
                client,
                country
            )
            for country in countries
        ]

        results = await asyncio.gather(
            *tasks
        )

    country_lookup = dict(
        zip(countries, results)
    )

    for record in records:

        country_info = country_lookup[
            record["country"]
        ]

        record.update(country_info)

    return records


# ============================================================
# CATEGORY SUMMARY
# ============================================================

def calculate_category_summary(
    records: list[dict[str, Any]]
) -> dict[str, Any]:

    category_groups = defaultdict(list)

    for record in records:

        category = record["category"]

        category_groups[category].append(record)

    summary = {}

    for category, items in category_groups.items():

        views = [
            item["views"]
            for item in items
        ]

        total_views = reduce(
            lambda x, y: x + y,
            views,
            0
        )

        average_views = (
            total_views / len(views)
        )

        summary[category] = {
            "video_count": len(items),
            "total_views": total_views,
            "average_views": round(
                average_views,
                2
            )
        }

    return summary


# ============================================================
# CREATOR SUMMARY
# ============================================================

def calculate_creator_summary(
    records: list[dict[str, Any]]
) -> dict[str, Any]:

    creator_groups = defaultdict(list)

    for record in records:

        creator = record["creator"]

        creator_groups[creator].append(record)

    summary = {}

    for creator, items in creator_groups.items():

        summary[creator] = {
            "video_count": len(items),
            "total_views": sum(
                item["views"]
                for item in items
            ),
            "average_duration": round(
                sum(
                    item["duration_minutes"]
                    for item in items
                ) / len(items),
                2
            )
        }

    return summary


# ============================================================
# QUALITY REPORT
# ============================================================

def calculate_quality_report(
    total_input: int,
    clean_records: int,
    rejected_records: int
) -> dict[str, Any]:

    rejection_rate = 0

    if total_input > 0:

        rejection_rate = (
            rejected_records /
            total_input
        ) * 100

    return {
        "total_input_records": total_input,
        "clean_records": clean_records,
        "rejected_records": rejected_records,
        "rejection_rate": round(
            rejection_rate,
            2
        )
    }


# ============================================================
# WRITE JSON
# ============================================================

def write_json(
    data: Any,
    output_file: Path
) -> None:

    with output_file.open(
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

def run_pipeline() -> None:

    logger.info(
        "MEDIA PIPELINE STARTED"
    )

    logger.info(
        "Operating system: %s",
        os.name
    )

    logger.info(
        "Python version: %s",
        sys.version
    )

    try:

        # ----------------------------------------------------
        # STEP 1 — DISCOVER
        # ----------------------------------------------------

        files = discover_files(
            SOURCE_DIR
        )

        # ----------------------------------------------------
        # STEP 2 — COUNT INPUT
        # ----------------------------------------------------

        total_input = 0

        for file_path in files:

            records = read_json(
                file_path
            )

            total_input += len(records)

        # ----------------------------------------------------
        # STEP 3 — VALIDATE + TRANSFORM
        # ----------------------------------------------------

        clean_records, rejected_records = (
            process_files(files)
        )

        # ----------------------------------------------------
        # STEP 4 — API ENRICHMENT
        # ----------------------------------------------------

        clean_records = asyncio.run(
            enrich_records(
                clean_records
            )
        )

        # ----------------------------------------------------
        # STEP 5 — ANALYTICS
        # ----------------------------------------------------

        category_summary = (
            calculate_category_summary(
                clean_records
            )
        )

        creator_summary = (
            calculate_creator_summary(
                clean_records
            )
        )

        quality_report = (
            calculate_quality_report(
                total_input,
                len(clean_records),
                rejected_records
            )
        )

        # ----------------------------------------------------
        # STEP 6 — SINK
        # ----------------------------------------------------

        write_json(
            clean_records,
            CLEAN_FILE
        )

        write_json(
            category_summary,
            CATEGORY_FILE
        )

        write_json(
            creator_summary,
            CREATOR_FILE
        )

        write_json(
            quality_report,
            QUALITY_FILE
        )

        # ----------------------------------------------------
        # STEP 7 — LOG RESULT
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
            rejected_records
        )

        logger.info(
            "MEDIA PIPELINE COMPLETED SUCCESSFULLY"
        )

    except Exception as error:

        logger.exception(
            "MEDIA PIPELINE FAILED: %s",
            error
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_pipeline()