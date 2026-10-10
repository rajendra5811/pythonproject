import json
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime


BASE = Path(__file__).parent

INPUT_DIR = BASE / "input"
OUTPUT_DIR = BASE / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


logging.basicConfig(
    filename=OUTPUT_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def discover_files():

    return list(INPUT_DIR.glob("*.json"))


def read_json(file):

    with file.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate(record):

    if record["usage_mb"] < 0:
        return False

    try:
        datetime.fromisoformat(record["timestamp"])
    except ValueError:
        return False

    return True


def transform(record):

    record["customer_id"] = record["customer_id"].strip().upper()
    record["tower_id"] = record["tower_id"].strip().upper()

    record["timestamp"] = datetime.fromisoformat(
        record["timestamp"]
    ).isoformat()

    return record


def process_files():

    valid_records = []
    rejected = 0

    for file in discover_files():

        logging.info("Reading %s", file.name)

        records = read_json(file)

        for record in records:

            if not validate(record):
                rejected += 1
                continue

            record = transform(record)

            valid_records.append(record)

    return valid_records, rejected


def customer_summary(records):

    result = defaultdict(int)

    for record in records:

        customer = record["customer_id"]

        result[customer] += record["usage_mb"]

    return dict(result)


def tower_summary(records):

    result = defaultdict(int)

    for record in records:

        tower = record["tower_id"]

        result[tower] += record["usage_mb"]

    return dict(result)


def write_json(filename, data):

    file = OUTPUT_DIR / filename

    with file.open("w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=2
        )


def run_pipeline():

    try:

        logging.info("PIPELINE STARTED")

        records, rejected = process_files()

        customers = customer_summary(records)

        towers = tower_summary(records)

        quality = {
            "valid_records": len(records),
            "rejected_records": rejected
        }

        write_json(
            "customer_summary.json",
            customers
        )

        write_json(
            "tower_summary.json",
            towers
        )

        write_json(
            "quality_report.json",
            quality
        )

        logging.info("PIPELINE COMPLETED")

    except Exception:

        logging.exception("PIPELINE FAILED")

        raise


if __name__ == "__main__":
    run_pipeline()