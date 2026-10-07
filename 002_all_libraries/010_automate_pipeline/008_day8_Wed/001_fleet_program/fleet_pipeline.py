from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from functools import reduce
from typing import Any
import json
import logging
import math
import os
import re
import sys


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

SOURCE_DIR = BASE_DIR / "fleet_data"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_FILE = OUTPUT_DIR / "clean_fleet_data.json"
SUMMARY_FILE = OUTPUT_DIR / "route_summary.json"
LOG_FILE = OUTPUT_DIR / "pipeline.log"


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
# VALIDATION
# ============================================================

def validate_record(record: dict[str, Any]) -> bool:

    required_fields = {
        "vehicle_id",
        "driver",
        "route",
        "latitude",
        "longitude",
        "speed",
        "fuel_level",
        "distance",
        "timestamp"
    }

    if not required_fields.issubset(record):
        return False

    if not record["vehicle_id"]:
        return False

    if not isinstance(record["speed"], (int, float)):
        return False

    if record["speed"] < 0:
        return False

    if not isinstance(record["fuel_level"], (int, float)):
        return False

    if not 0 <= record["fuel_level"] <= 100:
        return False

    if not isinstance(record["distance"], (int, float)):
        return False

    if record["distance"] < 0:
        return False

    if not -90 <= record["latitude"] <= 90:
        return False

    if not -180 <= record["longitude"] <= 180:
        return False

    if not re.match(
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
        record["timestamp"]
    ):
        return False

    return True


# ============================================================
# TRANSFORMATION
# ============================================================

def transform_record(record: dict[str, Any]) -> dict[str, Any]:

    cleaned = record.copy()

    cleaned["driver"] = (
        cleaned["driver"]
        .strip()
        .title()
    )

    cleaned["route"] = (
        cleaned["route"]
        .strip()
        .upper()
    )

    timestamp = datetime.strptime(
        cleaned["timestamp"],
        "%Y-%m-%d %H:%M:%S"
    )

    cleaned["timestamp"] = timestamp.isoformat()

    cleaned["speed"] = round(
        float(cleaned["speed"]),
        2
    )

    cleaned["fuel_level"] = round(
        float(cleaned["fuel_level"]),
        2
    )

    cleaned["distance"] = round(
        float(cleaned["distance"]),
        2
    )

    return cleaned


# ============================================================
# SOURCE
# ============================================================

def discover_files(source_dir: Path) -> list[Path]:

    if not source_dir.exists():
        raise FileNotFoundError(
            f"Source directory does not exist: {source_dir}"
        )

    files = list(source_dir.glob("*.json"))

    logger.info(
        "Discovered %d JSON files",
        len(files)
    )

    return files


# ============================================================
# READ JSON
# ============================================================

def read_json(file_path: Path) -> list[dict[str, Any]]:

    logger.info(
        "Reading file: %s",
        file_path.name
    )

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected list in {file_path.name}"
        )

    return data


# ============================================================
# EXTRACT + TRANSFORM
# ============================================================

def process_files(
    files: list[Path]
) -> list[dict[str, Any]]:

    clean_records = []

    for file_path in files:

        try:

            records = read_json(file_path)

            for record in records:

                if not validate_record(record):

                    logger.warning(
                        "Invalid record skipped: %s",
                        record.get("vehicle_id", "UNKNOWN")
                    )

                    continue

                clean_record = transform_record(record)

                clean_records.append(clean_record)

        except Exception as error:

            logger.exception(
                "Failed processing %s: %s",
                file_path.name,
                error
            )

    return clean_records


# ============================================================
# ROUTE ANALYTICS
# ============================================================

def calculate_route_summary(
    records: list[dict[str, Any]]
) -> dict[str, Any]:

    route_speeds = defaultdict(list)
    route_distances = defaultdict(list)
    route_count = Counter()

    for record in records:

        route = record["route"]

        route_speeds[route].append(
            record["speed"]
        )

        route_distances[route].append(
            record["distance"]
        )

        route_count[route] += 1

    summary = {}

    for route in route_count:

        speeds = route_speeds[route]
        distances = route_distances[route]

        average_speed = sum(speeds) / len(speeds)

        total_distance = reduce(
            lambda x, y: x + y,
            distances,
            0
        )

        summary[route] = {
            "record_count": route_count[route],
            "average_speed": round(
                average_speed,
                2
            ),
            "maximum_speed": max(speeds),
            "total_distance": round(
                total_distance,
                2
            ),
            "speed_variation": round(
                math.sqrt(
                    sum(
                        (x - average_speed) ** 2
                        for x in speeds
                    ) / len(speeds)
                ),
                2
            )
        }

    return summary


# ============================================================
# SINK
# ============================================================

def write_json(
    data: Any,
    output_file: Path
) -> None:

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

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


# ============================================================
# PIPELINE
# ============================================================

def run_pipeline() -> None:

    logger.info(
        "========== PIPELINE START =========="
    )

    logger.info(
        "Operating system: %s",
        os.name
    )

    logger.info(
        "Python version: %s",
        sys.version.split()[0]
    )

    try:

        # SOURCE
        files = discover_files(
            SOURCE_DIR
        )

        # EXTRACT + TRANSFORM
        clean_records = process_files(
            files
        )

        # ANALYTICS
        route_summary = calculate_route_summary(
            clean_records
        )

        # SINK
        write_json(
            clean_records,
            OUTPUT_FILE
        )

        write_json(
            route_summary,
            SUMMARY_FILE
        )

        logger.info(
            "Processed clean records: %d",
            len(clean_records)
        )

        logger.info(
            "========== PIPELINE SUCCESS =========="
        )

    except Exception as error:

        logger.exception(
            "PIPELINE FAILED: %s",
            error
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_pipeline()