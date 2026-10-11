from pathlib import Path
from datetime import datetime
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "biometric_events.json"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "biometric.db"
LOG_FILE = OUTPUT_DIR / "biometric_pipeline.log"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def is_valid_time(value):
    try:
        datetime.strptime(value, DATE_FORMAT)
        return True
    except (TypeError, ValueError):
        return False


def extract_events():
    logging.info("Extracting biometric events")

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("JSON root must be a list")

    logging.info("Extracted %d events", len(records))
    return records


def validate_events(records):
    valid_events = []
    rejected_events = []
    seen_punch_ids = set()

    for record in records:
        punch_id = record.get("punch_id")
        reason = None

        if not punch_id:
            reason = "Missing punch_id"
        elif punch_id in seen_punch_ids:
            reason = "Duplicate punch_id"
        elif not record.get("student_id"):
            reason = "Missing student_id"
        elif not record.get("device_id"):
            reason = "Missing device_id"
        elif not is_valid_time(record.get("punch_time")):
            reason = "Invalid punch_time"
        elif record.get("punch_type") not in ("IN", "OUT"):
            reason = "Invalid punch_type"

        if reason:
            rejected = dict(record)
            rejected["rejection_reason"] = reason
            rejected_events.append(rejected)
            continue

        valid_events.append(
            {
                "punch_id": punch_id,
                "student_id": record["student_id"],
                "device_id": record["device_id"],
                "punch_time": record["punch_time"],
                "punch_type": record["punch_type"],
            }
        )

        seen_punch_ids.add(punch_id)

    logging.info("Valid events: %d", len(valid_events))
    logging.info("Rejected events: %d", len(rejected_events))
    return valid_events, rejected_events


def create_database():
    connection = sqlite3.connect(DATABASE_FILE)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS biometric_events (
            punch_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            punch_time TEXT NOT NULL,
            punch_type TEXT NOT NULL,
            loaded_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS rejected_events (
            rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            punch_id TEXT,
            student_id TEXT,
            device_id TEXT,
            punch_time TEXT,
            punch_type TEXT,
            rejection_reason TEXT NOT NULL,
            rejected_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    return connection


def load_events(connection, valid_events, rejected_events):
    loaded_at = datetime.now().isoformat(timespec="seconds")

    valid_rows = [
        (
            event["punch_id"],
            event["student_id"],
            event["device_id"],
            event["punch_time"],
            event["punch_type"],
            loaded_at,
        )
        for event in valid_events
    ]

    connection.executemany(
        """
        INSERT INTO biometric_events (
            punch_id, student_id, device_id,
            punch_time, punch_type, loaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(punch_id)
        DO UPDATE SET
            student_id = excluded.student_id,
            device_id = excluded.device_id,
            punch_time = excluded.punch_time,
            punch_type = excluded.punch_type,
            loaded_at = excluded.loaded_at
        """,
        valid_rows,
    )

    rejected_rows = [
        (
            event.get("punch_id"),
            event.get("student_id"),
            event.get("device_id"),
            event.get("punch_time"),
            event.get("punch_type"),
            event["rejection_reason"],
            loaded_at,
        )
        for event in rejected_events
    ]

    connection.executemany(
        """
        INSERT INTO rejected_events (
            punch_id, student_id, device_id, punch_time,
            punch_type, rejection_reason, rejected_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rejected_rows,
    )

    connection.commit()


def create_attendance_report(connection):
    query = """
        SELECT
            student_id,
            SUBSTR(punch_time, 1, 10) AS attendance_date,
            MIN(
                CASE
                    WHEN punch_type = 'IN'
                    THEN punch_time
                END
            ) AS check_in_time,
            MAX(
                CASE
                    WHEN punch_type = 'OUT'
                    THEN punch_time
                END
            ) AS check_out_time,
            COUNT(*) AS punch_count,
            CASE
                WHEN COUNT(
                    CASE
                        WHEN punch_type = 'IN'
                        THEN 1
                    END
                ) > 0
                THEN 'Present'
                ELSE 'Incomplete'
            END AS attendance_status
        FROM biometric_events
        GROUP BY student_id, attendance_date
        ORDER BY attendance_date, student_id
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

    output_file = OUTPUT_DIR / "attendance_report.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    return records


def run_pipeline():
    setup_logging()
    connection = None

    try:
        records = extract_events()

        valid_events, rejected_events = validate_events(
            records
        )

        connection = create_database()

        connection.execute("BEGIN")

        load_events(
            connection,
            valid_events,
            rejected_events,
        )

        report = create_attendance_report(connection)

        connection.commit()

        print("Student biometric pipeline completed.")
        print(f"Input events: {len(records)}")
        print(f"Valid events: {len(valid_events)}")
        print(f"Rejected events: {len(rejected_events)}")
        print(f"Attendance records: {len(report)}")

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