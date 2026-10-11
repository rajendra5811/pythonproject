from pathlib import Path
from datetime import datetime
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "cdrs.json"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "telecom.db"
LOG_FILE = OUTPUT_DIR / "telecom_pipeline.log"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

VALID_TYPES = {"Voice", "Data", "SMS"}
VALID_STATUSES = {"Completed", "Dropped", "Failed"}


def setup_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format=(
            "%(asctime)s - "
            "%(levelname)s - "
            "%(message)s"
        ),
    )


def parse_datetime(value):
    try:
        datetime.strptime(value, DATE_FORMAT)
        return True
    except (TypeError, ValueError):
        return False


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_cdrs():
    logging.info("Extracting CDRs")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(
            "JSON root must contain a list"
        )

    logging.info(
        "Extracted %d records",
        len(records),
    )

    return records


def validate_cdrs(records):
    logging.info("Validating CDRs")

    valid_records = []
    rejected_records = []
    seen_ids = set()

    for record in records:
        cdr_id = record.get("cdr_id")
        reason = None

        if not cdr_id:
            reason = "Missing cdr_id"

        elif cdr_id in seen_ids:
            reason = "Duplicate cdr_id"

        elif not record.get("msisdn"):
            reason = "Missing msisdn"

        elif not record.get("cell_id"):
            reason = "Missing cell_id"

        elif not parse_datetime(
            record.get("event_time")
        ):
            reason = "Invalid event_time"

        elif record.get("call_type") not in VALID_TYPES:
            reason = "Invalid call_type"

        elif record.get("call_status") not in VALID_STATUSES:
            reason = "Invalid call_status"

        else:
            duration = to_integer(
                record.get("duration_seconds")
            )

            data_volume = to_float(
                record.get("data_volume_mb")
            )

            latency = to_integer(
                record.get("latency_ms")
            )

            charge = to_float(
                record.get("charge_amount")
            )

            if duration is None or duration < 0:
                reason = "Invalid duration_seconds"

            elif data_volume is None or data_volume < 0:
                reason = "Invalid data_volume_mb"

            elif latency is None or latency < 0:
                reason = "Invalid latency_ms"

            elif charge is None or charge < 0:
                reason = "Invalid charge_amount"

        if reason:
            rejected = dict(record)
            rejected["rejection_reason"] = reason
            rejected_records.append(rejected)
            continue

        valid_records.append(
            {
                "cdr_id": cdr_id,
                "msisdn": record["msisdn"],
                "cell_id": record["cell_id"],
                "event_time": record["event_time"],
                "call_type": record["call_type"],
                "call_status": record["call_status"],
                "duration_seconds": to_integer(
                    record["duration_seconds"]
                ),
                "data_volume_mb": to_float(
                    record["data_volume_mb"]
                ),
                "latency_ms": to_integer(
                    record["latency_ms"]
                ),
                "charge_amount": to_float(
                    record["charge_amount"]
                ),
            }
        )

        seen_ids.add(cdr_id)

    logging.info(
        "Valid records: %d",
        len(valid_records),
    )

    logging.info(
        "Rejected records: %d",
        len(rejected_records),
    )

    return valid_records, rejected_records


def create_database():
    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS cdrs (
            cdr_id TEXT PRIMARY KEY,
            msisdn TEXT NOT NULL,
            cell_id TEXT NOT NULL,
            event_time TEXT NOT NULL,
            call_type TEXT NOT NULL,
            call_status TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            data_volume_mb REAL NOT NULL,
            latency_ms INTEGER NOT NULL,
            charge_amount REAL NOT NULL
        )
        """
    )

    connection.commit()

    return connection


def load_cdrs(connection, records):
    if not records:
        return

    rows = []

    for record in records:
        rows.append(
            (
                record["cdr_id"],
                record["msisdn"],
                record["cell_id"],
                record["event_time"],
                record["call_type"],
                record["call_status"],
                record["duration_seconds"],
                record["data_volume_mb"],
                record["latency_ms"],
                record["charge_amount"],
            )
        )

    connection.executemany(
        """
        INSERT INTO cdrs (
            cdr_id,
            msisdn,
            cell_id,
            event_time,
            call_type,
            call_status,
            duration_seconds,
            data_volume_mb,
            latency_ms,
            charge_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(cdr_id)
        DO UPDATE SET
            msisdn = excluded.msisdn,
            cell_id = excluded.cell_id,
            event_time = excluded.event_time,
            call_type = excluded.call_type,
            call_status = excluded.call_status,
            duration_seconds =
                excluded.duration_seconds,
            data_volume_mb =
                excluded.data_volume_mb,
            latency_ms = excluded.latency_ms,
            charge_amount = excluded.charge_amount
        """,
        rows,
    )

    connection.commit()

    logging.info(
        "Loaded %d CDRs",
        len(rows),
    )


def create_network_report(connection):
    logging.info("Creating network report")

    query = """
        SELECT
            cell_id,
            COUNT(*) AS total_cdrs,
            COUNT(
                CASE
                    WHEN call_type = 'Voice'
                    THEN 1
                END
            ) AS voice_calls,
            COUNT(
                CASE
                    WHEN call_status = 'Dropped'
                    THEN 1
                END
            ) AS dropped_calls,
            ROUND(
                100.0
                * COUNT(
                    CASE
                        WHEN call_status = 'Dropped'
                        THEN 1
                    END
                )
                / NULLIF(
                    COUNT(
                        CASE
                            WHEN call_status = 'Completed'
                            THEN 1
                        END
                    ),
                    0
                ),
                2
            ) AS call_drop_rate_percentage,
            ROUND(AVG(latency_ms), 2)
                AS average_latency_ms,
            ROUND(SUM(data_volume_mb), 2)
                AS total_data_volume_mb,
            ROUND(SUM(charge_amount), 2)
                AS total_revenue
        FROM cdrs
        GROUP BY cell_id
        ORDER BY cell_id
    """

    cursor = connection.execute(query)

    columns = [
        description[0]
        for description in cursor.description
    ]

    rows = cursor.fetchall()

    records = [
        dict(zip(columns, row))
        for row in rows
    ]

    output_file = OUTPUT_DIR / "cell_performance.json"

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            records,
            file,
            indent=4,
            default=str,
        )

    return records


def run_pipeline():
    setup_logging()

    connection = None

    try:
        records = extract_cdrs()

        valid_records, rejected_records = (
            validate_cdrs(records)
        )

        connection = create_database()

        connection.execute("BEGIN")

        load_cdrs(
            connection,
            valid_records,
        )

        report = create_network_report(
            connection
        )

        connection.commit()

        print(
            "Telecom pipeline completed successfully."
        )
        print(f"Input CDRs: {len(records)}")
        print(
            f"Valid CDRs: {len(valid_records)}"
        )
        print(
            f"Rejected CDRs: {len(rejected_records)}"
        )
        print(
            f"Cells processed: {len(report)}"
        )
        print(f"Database: {DATABASE_FILE}")

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