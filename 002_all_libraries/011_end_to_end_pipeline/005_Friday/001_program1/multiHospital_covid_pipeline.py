from pathlib import Path
from datetime import datetime
import json
import logging
import shutil
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
INCOMING_DIR = BASE_DIR / "data" / "incoming"
PROCESSED_DIR = BASE_DIR / "processed"
REJECTED_DIR = BASE_DIR / "rejected"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "covid_reporting.db"
LOG_FILE = OUTPUT_DIR / "multi_hospital_pipeline.log"

DATE_FORMAT = "%Y-%m-%d"


def setup_logging():
    for folder in [
        INCOMING_DIR,
        PROCESSED_DIR,
        REJECTED_DIR,
        OUTPUT_DIR,
    ]:
        folder.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def is_valid_date(value):
    try:
        datetime.strptime(value, DATE_FORMAT)
        return True
    except (TypeError, ValueError):
        return False


def to_integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def validate_report(record):
    required_fields = [
        "report_id",
        "hospital_code",
        "report_date",
        "state_code",
        "district_code",
        "tests_conducted",
        "positive_cases",
        "recoveries",
        "deaths",
        "active_cases",
        "total_beds",
        "occupied_beds",
        "oxygen_beds",
        "oxygen_beds_occupied",
        "icu_beds",
        "icu_beds_occupied",
        "ventilators",
        "ventilators_in_use",
    ]

    for field in required_fields:
        if record.get(field) is None:
            return f"Missing {field}"

    if not is_valid_date(record["report_date"]):
        return "Invalid report_date"

    numeric_fields = required_fields[5:]

    for field in numeric_fields:
        value = to_integer(record[field])

        if value is None or value < 0:
            return f"Invalid {field}"

    if record["positive_cases"] > record["tests_conducted"]:
        return "Positive cases exceed tests conducted"

    if record["occupied_beds"] > record["total_beds"]:
        return "Occupied beds exceed total beds"

    if record["oxygen_beds_occupied"] > record["oxygen_beds"]:
        return "Occupied oxygen beds exceed available beds"

    if record["icu_beds_occupied"] > record["icu_beds"]:
        return "Occupied ICU beds exceed available beds"

    if record["ventilators_in_use"] > record["ventilators"]:
        return "Ventilators in use exceed available ventilators"

    return None


def create_database():
    connection = sqlite3.connect(DATABASE_FILE)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS hospital_daily_reports (
            report_id TEXT PRIMARY KEY,
            hospital_code TEXT NOT NULL,
            report_date TEXT NOT NULL,
            state_code TEXT NOT NULL,
            district_code TEXT NOT NULL,
            tests_conducted INTEGER NOT NULL,
            positive_cases INTEGER NOT NULL,
            recoveries INTEGER NOT NULL,
            deaths INTEGER NOT NULL,
            active_cases INTEGER NOT NULL,
            total_beds INTEGER NOT NULL,
            occupied_beds INTEGER NOT NULL,
            oxygen_beds INTEGER NOT NULL,
            oxygen_beds_occupied INTEGER NOT NULL,
            icu_beds INTEGER NOT NULL,
            icu_beds_occupied INTEGER NOT NULL,
            ventilators INTEGER NOT NULL,
            ventilators_in_use INTEGER NOT NULL,
            source_file TEXT NOT NULL,
            loaded_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS rejected_reports (
            rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT,
            hospital_code TEXT,
            report_date TEXT,
            state_code TEXT,
            district_code TEXT,
            source_file TEXT NOT NULL,
            rejection_reason TEXT NOT NULL,
            rejected_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    return connection


def load_valid_report(connection, record, source_file):
    loaded_at = datetime.now().isoformat(timespec="seconds")

    connection.execute(
        """
        INSERT INTO hospital_daily_reports (
            report_id, hospital_code, report_date,
            state_code, district_code,
            tests_conducted, positive_cases,
            recoveries, deaths, active_cases,
            total_beds, occupied_beds,
            oxygen_beds, oxygen_beds_occupied,
            icu_beds, icu_beds_occupied,
            ventilators, ventilators_in_use,
            source_file, loaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(report_id)
        DO UPDATE SET
            hospital_code = excluded.hospital_code,
            report_date = excluded.report_date,
            state_code = excluded.state_code,
            district_code = excluded.district_code,
            tests_conducted = excluded.tests_conducted,
            positive_cases = excluded.positive_cases,
            recoveries = excluded.recoveries,
            deaths = excluded.deaths,
            active_cases = excluded.active_cases,
            total_beds = excluded.total_beds,
            occupied_beds = excluded.occupied_beds,
            oxygen_beds = excluded.oxygen_beds,
            oxygen_beds_occupied = excluded.oxygen_beds_occupied,
            icu_beds = excluded.icu_beds,
            icu_beds_occupied = excluded.icu_beds_occupied,
            ventilators = excluded.ventilators,
            ventilators_in_use = excluded.ventilators_in_use,
            source_file = excluded.source_file,
            loaded_at = excluded.loaded_at
        """,
        (
            record["report_id"],
            record["hospital_code"],
            record["report_date"],
            record["state_code"],
            record["district_code"],
            record["tests_conducted"],
            record["positive_cases"],
            record["recoveries"],
            record["deaths"],
            record["active_cases"],
            record["total_beds"],
            record["occupied_beds"],
            record["oxygen_beds"],
            record["oxygen_beds_occupied"],
            record["icu_beds"],
            record["icu_beds_occupied"],
            record["ventilators"],
            record["ventilators_in_use"],
            source_file,
            loaded_at,
        ),
    )


def load_rejected_report(
    connection,
    record,
    source_file,
    reason,
):
    rejected_at = datetime.now().isoformat(
        timespec="seconds"
    )

    connection.execute(
        """
        INSERT INTO rejected_reports (
            report_id, hospital_code, report_date,
            state_code, district_code, source_file,
            rejection_reason, rejected_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.get("report_id"),
            record.get("hospital_code"),
            record.get("report_date"),
            record.get("state_code"),
            record.get("district_code"),
            source_file,
            reason,
            rejected_at,
        ),
    )


def process_hospital_file(connection, file_path):
    logging.info("Processing %s", file_path.name)

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            record = json.load(file)

        reason = validate_report(record)

        if reason:
            load_rejected_report(
                connection,
                record,
                file_path.name,
                reason,
            )

            shutil.move(
                file_path,
                REJECTED_DIR / file_path.name,
            )

            logging.warning(
                "Rejected %s: %s",
                file_path.name,
                reason,
            )

            return False

        load_valid_report(
            connection,
            record,
            file_path.name,
        )

        shutil.move(
            file_path,
            PROCESSED_DIR / file_path.name,
        )

        logging.info(
            "Processed %s successfully",
            file_path.name,
        )

        return True

    except Exception as error:
        logging.exception(
            "Failed to process %s: %s",
            file_path.name,
            error,
        )

        shutil.move(
            file_path,
            REJECTED_DIR / file_path.name,
        )

        return False


def create_government_report(connection):
    query = """
        SELECT
            report_date,
            state_code,
            district_code,
            COUNT(DISTINCT hospital_code)
                AS reporting_hospitals,
            SUM(tests_conducted) AS tests_conducted,
            SUM(positive_cases) AS positive_cases,
            SUM(recoveries) AS recoveries,
            SUM(deaths) AS deaths,
            SUM(active_cases) AS active_cases,
            SUM(total_beds) AS total_beds,
            SUM(occupied_beds) AS occupied_beds,
            SUM(oxygen_beds) AS oxygen_beds,
            SUM(oxygen_beds_occupied)
                AS oxygen_beds_occupied,
            SUM(icu_beds) AS icu_beds,
            SUM(icu_beds_occupied)
                AS icu_beds_occupied,
            SUM(ventilators) AS ventilators,
            SUM(ventilators_in_use)
                AS ventilators_in_use,
            ROUND(
                100.0 * SUM(positive_cases)
                / NULLIF(SUM(tests_conducted), 0),
                2
            ) AS positivity_rate_percentage,
            ROUND(
                100.0 * SUM(occupied_beds)
                / NULLIF(SUM(total_beds), 0),
                2
            ) AS bed_occupancy_percentage
        FROM hospital_daily_reports
        GROUP BY report_date, state_code, district_code
        ORDER BY report_date, state_code, district_code
    """

    cursor = connection.execute(query)

    columns = [
        description[0]
        for description in cursor.description
    ]

    records = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

    output_file = (
        OUTPUT_DIR
        / "government_daily_report.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            records,
            file,
            indent=4,
        )

    return records


def run_pipeline():
    setup_logging()

    connection = None

    try:
        files = sorted(
            INCOMING_DIR.glob("*.json")
        )

        if not files:
            logging.info("No hospital files found")
            print("No hospital files found.")
            return

        connection = create_database()

        connection.execute("BEGIN")

        valid_count = 0
        rejected_count = 0

        for file_path in files:
            processed = process_hospital_file(
                connection,
                file_path,
            )

            if processed:
                valid_count += 1
            else:
                rejected_count += 1

        report = create_government_report(
            connection
        )

        connection.commit()

        print(
            "Multi-hospital COVID pipeline completed."
        )
        print(f"Hospital files found: {len(files)}")
        print(f"Valid reports: {valid_count}")
        print(f"Rejected reports: {rejected_count}")
        print(f"Government report rows: {len(report)}")

    except Exception as error:
        if connection is not None:
            connection.rollback()

        logging.exception(
            "Pipeline failed: %s",
            error,
        )

        print(f"Pipeline failed: {error}")

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    run_pipeline()