import json
import logging
from pathlib import Path
from collections import defaultdict


# ==================================================
# 1. CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==================================================
# 2. LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==================================================
# 3. SOURCE — DISCOVER FILES
# ==================================================

def discover_files():

    return list(INPUT_DIR.glob("*.json"))


# ==================================================
# 4. SOURCE — READ JSON
# ==================================================

def read_json(file_path):

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==================================================
# 5. VALIDATION
# ==================================================

def validate(record):

    if record["generated_kwh"] < 0:

        logger.warning(
            "Invalid record: %s",
            record["plant_id"]
        )

        return False

    if record["consumed_kwh"] < 0:

        return False

    return True


# ==================================================
# 6. TRANSFORMATION
# ==================================================

def transform(record):

    record["city"] = record["city"].strip().upper()

    generated = record["generated_kwh"]
    consumed = record["consumed_kwh"]

    utilization = 0

    if generated > 0:

        utilization = (
            consumed / generated
        ) * 100

    record["utilization"] = round(
        utilization,
        2
    )

    return record


# ==================================================
# 7. AGGREGATION
# ==================================================

def aggregate(records):

    summary = defaultdict(
        lambda: {
            "generated_kwh": 0,
            "consumed_kwh": 0,
            "records": 0
        }
    )

    for record in records:

        plant = record["plant_id"]

        summary[plant]["generated_kwh"] += (
            record["generated_kwh"]
        )

        summary[plant]["consumed_kwh"] += (
            record["consumed_kwh"]
        )

        summary[plant]["records"] += 1

    return dict(summary)


# ==================================================
# 8. SINK — WRITE JSON
# ==================================================

def write_output(data):

    output_file = (
        OUTPUT_DIR /
        "solar_summary.json"
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
        "Output written successfully"
    )


# ==================================================
# 9. PIPELINE
# ==================================================

def run_pipeline():

    logger.info(
        "Solar pipeline started"
    )

    all_records = []

    files = discover_files()

    for file_path in files:

        records = read_json(file_path)

        for record in records:

            if validate(record):

                record = transform(record)

                all_records.append(record)

    summary = aggregate(
        all_records
    )

    write_output(summary)

    logger.info(
        "Solar pipeline completed"
    )


# ==================================================
# 10. ENTRY POINT
# ==================================================

if __name__ == "__main__":

    run_pipeline()