from pathlib import Path
from datetime import datetime
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "hospital_daily_data.json"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "covid_reporting.db"
LOG_FILE = OUTPUT_DIR / "covid_reporting_pipeline.log"
DATE_FORMAT = "%Y-%m-%d"


def setup_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)

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


def extract_reports():
    logging.info("Extracting hospital daily reports")

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("JSON root must be a list")

    logging.info("Extracted %d reports", len(records))
    return records


def validate_reports(records):
    valid_reports = []
    rejected_reports = []
    seen_report_ids = set()

    for record in records:
        report_id = record.get("report_id")
        reason = None

        if not report_id:
            reason = "Missing report_id"
        elif report_id in seen_report_ids:
            reason = "Duplicate report_id"
        elif not record.get("hospital_code"):
            reason = "Missing hospital_code"
        elif not is_valid_date(record.get("report_date")):
            reason = "Invalid report_date"
        elif not record.get("state_code"):
            reason = "Missing state_code"
        elif not record.get("district_code"):
            reason = "Missing district_code"
        else:
            fields = [
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

            for field in fields:
                value = to_integer(record.get(field))

                if value is None or value < 0:
                    reason = f"Invalid {field}"
                    break

            if reason is None:
                if record["positive_cases"] > record["tests_conducted"]:
                    reason = "Positive cases exceed tests conducted"

                elif record["occupied_beds"] > record["total_beds"]:
                    reason = "Occupied beds exceed total beds"

                elif record["oxygen_beds_occupied"] > record["oxygen_beds"]:
                    reason = "Occupied oxygen beds exceed available oxygen beds"

                elif record["icu_beds_occupied"] > record["icu_beds"]:
                    reason = "Occupied ICU beds exceed available ICU beds"

                elif record["ventilators_in_use"] > record["ventilators"]:
                    reason = "Ventilators in use exceed available ventilators"

        if reason:
            rejected = dict(record)
            rejected["rejection_reason"] = reason
            rejected_reports.append(rejected)
            continue

        valid_reports.append(record)
        seen_report_ids.add(report_id)

    logging.info("Valid reports: %d", len(valid_reports))
    logging.info("Rejected reports: %d", len(rejected_reports))
    return valid_reports, rejected_reports


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
            rejection_reason TEXT NOT NULL,
            rejected_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    return connection


def load_reports(connection, valid_reports, rejected_reports):
    loaded_at = datetime.now().isoformat(timespec="seconds")

    valid_rows = [
        (
            report["report_id"],
            report["hospital_code"],
            report["report_date"],
            report["state_code"],
            report["district_code"],
            report["tests_conducted"],
            report["positive_cases"],
            report["recoveries"],
            report["deaths"],
            report["active_cases"],
            report["total_beds"],
            report["occupied_beds"],
            report["oxygen_beds"],
            report["oxygen_beds_occupied"],
            report["icu_beds"],
            report["icu_beds_occupied"],
            report["ventilators"],
            report["ventilators_in_use"],
            loaded_at,
        )
        for report in valid_reports
    ]

    connection.executemany(
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
            loaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            loaded_at = excluded.loaded_at
        """,
        valid_rows,
    )

    rejected_rows = [
        (
            report.get("report_id"),
            report.get("hospital_code"),
            report.get("report_date"),
            report.get("state_code"),
            report.get("district_code"),
            report["rejection_reason"],
            loaded_at,
        )
        for report in rejected_reports
    ]

    connection.executemany(
        """
        INSERT INTO rejected_reports (
            report_id, hospital_code, report_date,
            state_code, district_code,
            rejection_reason, rejected_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rejected_rows,
    )

    connection.commit()


def create_government_report(connection):
    query = """
        SELECT
            report_date,
            state_code,
            district_code,
            COUNT(DISTINCT hospital_code) AS reporting_hospitals,
            SUM(tests_conducted) AS tests_conducted,
            SUM(positive_cases) AS positive_cases,
            SUM(recoveries) AS recoveries,
            SUM(deaths) AS deaths,
            SUM(active_cases) AS active_cases,
            SUM(total_beds) AS total_beds,
            SUM(occupied_beds) AS occupied_beds,
            SUM(oxygen_beds) AS oxygen_beds,
            SUM(oxygen_beds_occupied) AS oxygen_beds_occupied,
            SUM(icu_beds) AS icu_beds,
            SUM(icu_beds_occupied) AS icu_beds_occupied,
            SUM(ventilators) AS ventilators,
            SUM(ventilators_in_use) AS ventilators_in_use,
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

    output_file = OUTPUT_DIR / "government_daily_report.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    return records


def run_pipeline():
    setup_logging()
    connection = None

    try:
        records = extract_reports()

        valid_reports, rejected_reports = validate_reports(
            records
        )

        connection = create_database()

        connection.execute("BEGIN")

        load_reports(
            connection,
            valid_reports,
            rejected_reports,
        )

        report = create_government_report(connection)

        connection.commit()

        print("COVID reporting pipeline completed.")
        print(f"Input reports: {len(records)}")
        print(f"Valid reports: {len(valid_reports)}")
        print(f"Rejected reports: {len(rejected_reports)}")
        print(f"Government report rows: {len(report)}")

    except Exception as error:
        if connection is not None:
            connection.rollback()

        logging.exception("Pipeline failed: %s", error)
        print(f"Pipeline failed: {error}")

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    run_pipeline()