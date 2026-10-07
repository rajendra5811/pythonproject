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

SOURCE_DIR = BASE_DIR / "delivery_data"
OUTPUT_DIR = BASE_DIR / "output"

CLEAN_DATA_FILE = OUTPUT_DIR / "clean_deliveries.json"
SUMMARY_FILE = OUTPUT_DIR / "delivery_summary.json"
DRIVER_FILE = OUTPUT_DIR / "driver_summary.json"
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

def validate_delivery(
    delivery: dict[str, Any]
) -> bool:

    required_fields = {
        "delivery_id",
        "driver_id",
        "vehicle_id",
        "customer",
        "city",
        "route",
        "distance_km",
        "delivery_time_minutes",
        "fuel_used_litres",
        "status",
        "delivery_date"
    }

    if not required_fields.issubset(delivery):
        return False

    if not delivery["delivery_id"]:
        return False

    if not delivery["driver_id"]:
        return False

    if not delivery["vehicle_id"]:
        return False

    if not isinstance(
        delivery["distance_km"],
        (int, float)
    ):
        return False

    if delivery["distance_km"] <= 0:
        return False

    if not isinstance(
        delivery["delivery_time_minutes"],
        (int, float)
    ):
        return False

    if delivery["delivery_time_minutes"] <= 0:
        return False

    if not isinstance(
        delivery["fuel_used_litres"],
        (int, float)
    ):
        return False

    if delivery["fuel_used_litres"] <= 0:
        return False

    if delivery["status"] not in {
        "delivered",
        "cancelled",
        "failed"
    }:
        return False

    if not re.match(
        r"^\d{4}-\d{2}-\d{2} "
        r"\d{2}:\d{2}:\d{2}$",
        delivery["delivery_date"]
    ):
        return False

    return True


# ============================================================
# TRANSFORMATION
# ============================================================

def transform_delivery(
    delivery: dict[str, Any]
) -> dict[str, Any]:

    cleaned = delivery.copy()

    # Clean customer
    cleaned["customer"] = (
        cleaned["customer"]
        .strip()
        .title()
    )

    # Normalize city
    cleaned["city"] = (
        cleaned["city"]
        .strip()
        .upper()
    )

    # Normalize route
    cleaned["route"] = (
        cleaned["route"]
        .strip()
        .upper()
    )

    # Convert date
    delivery_date = datetime.strptime(
        cleaned["delivery_date"],
        "%Y-%m-%d %H:%M:%S"
    )

    cleaned["delivery_date"] = (
        delivery_date.isoformat()
    )

    # Normalize numeric values
    cleaned["distance_km"] = round(
        float(cleaned["distance_km"]),
        2
    )

    cleaned["delivery_time_minutes"] = round(
        float(cleaned["delivery_time_minutes"]),
        2
    )

    cleaned["fuel_used_litres"] = round(
        float(cleaned["fuel_used_litres"]),
        2
    )

    # Calculate fuel efficiency
    cleaned["fuel_efficiency"] = round(
        cleaned["distance_km"]
        / cleaned["fuel_used_litres"],
        2
    )

    return cleaned


# ============================================================
# FILE DISCOVERY
# ============================================================

def discover_files(
    source_dir: Path
) -> list[Path]:

    if not source_dir.exists():
        raise FileNotFoundError(
            f"Directory not found: {source_dir}"
        )

    files = list(
        source_dir.glob("*.json")
    )

    logger.info(
        "Discovered %d JSON files",
        len(files)
    )

    return files


# ============================================================
# JSON READING
# ============================================================

def read_json(
    file_path: Path
) -> list[dict[str, Any]]:

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
# PROCESS FILES
# ============================================================

def process_files(
    files: list[Path]
) -> list[dict[str, Any]]:

    clean_deliveries = []

    for file_path in files:

        try:

            deliveries = read_json(
                file_path
            )

            for delivery in deliveries:

                if not validate_delivery(
                    delivery
                ):

                    logger.warning(
                        "Invalid delivery skipped: %s",
                        delivery.get(
                            "delivery_id",
                            "UNKNOWN"
                        )
                    )

                    continue

                clean_delivery = (
                    transform_delivery(
                        delivery
                    )
                )

                clean_deliveries.append(
                    clean_delivery
                )

        except Exception as error:

            logger.exception(
                "Failed processing %s: %s",
                file_path.name,
                error
            )

    return clean_deliveries


# ============================================================
# ROUTE ANALYTICS
# ============================================================

def calculate_route_summary(
    deliveries: list[dict[str, Any]]
) -> dict[str, Any]:

    route_times = defaultdict(list)
    route_distances = defaultdict(list)

    route_counter = Counter()

    for delivery in deliveries:

        route = delivery["route"]

        route_times[route].append(
            delivery[
                "delivery_time_minutes"
            ]
        )

        route_distances[route].append(
            delivery["distance_km"]
        )

        route_counter[route] += 1

    summary = {}

    for route in route_counter:

        times = route_times[route]
        distances = route_distances[route]

        average_time = (
            sum(times) / len(times)
        )

        total_distance = reduce(
            lambda x, y: x + y,
            distances,
            0
        )

        summary[route] = {
            "delivery_count":
                route_counter[route],

            "average_delivery_time":
                round(
                    average_time,
                    2
                ),

            "total_distance_km":
                round(
                    total_distance,
                    2
                ),

            "maximum_delivery_time":
                max(times),

            "minimum_delivery_time":
                min(times)
        }

    return summary


# ============================================================
# DRIVER ANALYTICS
# ============================================================

def calculate_driver_summary(
    deliveries: list[dict[str, Any]]
) -> dict[str, Any]:

    driver_data = defaultdict(list)

    for delivery in deliveries:

        driver_id = delivery[
            "driver_id"
        ]

        driver_data[
            driver_id
        ].append(delivery)

    summary = {}

    for driver_id, records in (
        driver_data.items()
    ):

        total_distance = sum(
            record["distance_km"]
            for record in records
        )

        average_time = sum(
            record[
                "delivery_time_minutes"
            ]
            for record in records
        ) / len(records)

        summary[driver_id] = {
            "delivery_count": len(records),

            "total_distance_km": round(
                total_distance,
                2
            ),

            "average_delivery_time":
                round(
                    average_time,
                    2
                ),

            "average_fuel_efficiency":
                round(
                    sum(
                        record[
                            "fuel_efficiency"
                        ]
                        for record in records
                    ) / len(records),
                    2
                )
        }

    return summary


# ============================================================
# CITY ANALYTICS
# ============================================================

def calculate_city_summary(
    deliveries: list[dict[str, Any]]
) -> dict[str, int]:

    cities = [
        delivery["city"]
        for delivery in deliveries
    ]

    return dict(
        Counter(cities)
    )


# ============================================================
# QUALITY METRICS
# ============================================================

def calculate_quality_metrics(
    total_input: int,
    total_clean: int
) -> dict[str, Any]:

    rejected = (
        total_input - total_clean
    )

    if total_input == 0:
        rejection_rate = 0
    else:
        rejection_rate = (
            rejected / total_input
        ) * 100

    return {
        "input_records": total_input,
        "clean_records": total_clean,
        "rejected_records": rejected,
        "rejection_rate_percent": round(
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
# MAIN PIPELINE
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

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        files = discover_files(
            SOURCE_DIR
        )

        # ----------------------------------------------------
        # EXTRACT + TRANSFORM
        # ----------------------------------------------------

        deliveries = []

        total_input = 0

        for file_path in files:

            records = read_json(
                file_path
            )

            total_input += len(records)

        deliveries = process_files(
            files
        )

        # ----------------------------------------------------
        # ANALYTICS
        # ----------------------------------------------------

        route_summary = (
            calculate_route_summary(
                deliveries
            )
        )

        driver_summary = (
            calculate_driver_summary(
                deliveries
            )
        )

        city_summary = (
            calculate_city_summary(
                deliveries
            )
        )

        quality_metrics = (
            calculate_quality_metrics(
                total_input,
                len(deliveries)
            )
        )

        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        write_json(
            deliveries,
            CLEAN_DATA_FILE
        )

        write_json(
            {
                "routes": route_summary,
                "cities": city_summary,
                "quality": quality_metrics
            },
            SUMMARY_FILE
        )

        write_json(
            driver_summary,
            DRIVER_FILE
        )

        # ----------------------------------------------------
        # FINAL LOG
        # ----------------------------------------------------

        logger.info(
            "Input records: %d",
            total_input
        )

        logger.info(
            "Clean records: %d",
            len(deliveries)
        )

        logger.info(
            "Rejected records: %d",
            quality_metrics[
                "rejected_records"
            ]
        )

        logger.info(
            "========== PIPELINE SUCCESS =========="
        )

    except Exception as error:

        logger.exception(
            "========== PIPELINE FAILED ==========: %s",
            error
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_pipeline()