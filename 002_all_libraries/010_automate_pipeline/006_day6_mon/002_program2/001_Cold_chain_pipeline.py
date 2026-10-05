from pathlib import Path
from datetime import datetime
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "cold_chain_events.json"
)

OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "cold_chain.db"
LOG_FILE = OUTPUT_DIR / "cold_chain_pipeline.log"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

MIN_TEMPERATURE = 2.0
MAX_TEMPERATURE = 8.0
MAX_HUMIDITY = 85.0
MIN_BATTERY_LEVEL = 20


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


def extract_events():
    logging.info("Starting cold-chain extraction")

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
            "The JSON root must contain a list"
        )

    logging.info(
        "Extracted %d events",
        len(records),
    )

    return records


def validate_events(records):
    logging.info("Starting event validation")

    valid_events = []
    rejected_events = []
    seen_event_ids = set()

    for record in records:
        event_id = record.get("event_id")
        shipment_id = record.get("shipment_id")
        device_id = record.get("device_id")
        event_time = record.get("event_time")
        event_type = record.get("event_type")

        temperature = to_float(
            record.get("temperature")
        )

        humidity = to_float(
            record.get("humidity")
        )

        door_open = to_integer(
            record.get("door_open")
        )

        battery_level = to_integer(
            record.get("battery_level")
        )

        reason = None

        if not event_id:
            reason = "Missing event_id"

        elif event_id in seen_event_ids:
            reason = "Duplicate event_id"

        elif not shipment_id:
            reason = "Missing shipment_id"

        elif not device_id:
            reason = "Missing device_id"

        elif not parse_datetime(event_time):
            reason = "Invalid event_time"

        elif event_type not in (
            "Temperature",
            "Door",
        ):
            reason = "Invalid event_type"

        elif temperature is None:
            reason = "Invalid temperature"

        elif humidity is None:
            reason = "Invalid humidity"

        elif not 0 <= humidity <= 100:
            reason = "Humidity must be between 0 and 100"

        elif door_open not in (0, 1):
            reason = "door_open must be 0 or 1"

        elif battery_level is None:
            reason = "Invalid battery_level"

        elif not 0 <= battery_level <= 100:
            reason = (
                "battery_level must be between 0 and 100"
            )

        if reason:
            rejected_event = dict(record)
            rejected_event["rejection_reason"] = reason
            rejected_events.append(rejected_event)
            continue

        valid_event = {
            "event_id": event_id,
            "shipment_id": shipment_id,
            "device_id": device_id,
            "event_time": event_time,
            "event_type": event_type,
            "temperature": temperature,
            "humidity": humidity,
            "door_open": door_open,
            "battery_level": battery_level,
            "location": record.get(
                "location",
                "Unknown",
            ),
        }

        valid_events.append(valid_event)
        seen_event_ids.add(event_id)

    logging.info(
        "Valid events: %d",
        len(valid_events),
    )

    logging.info(
        "Rejected events: %d",
        len(rejected_events),
    )

    return valid_events, rejected_events


def create_database():
    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.execute(
        """
        PRAGMA journal_mode = WAL
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS cold_chain_events (
            event_id TEXT PRIMARY KEY,
            shipment_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            event_time TEXT NOT NULL,
            event_type TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            door_open INTEGER NOT NULL,
            battery_level INTEGER NOT NULL,
            location TEXT NOT NULL,
            loaded_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS rejected_events (
            rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            shipment_id TEXT,
            device_id TEXT,
            event_time TEXT,
            event_type TEXT,
            temperature REAL,
            humidity REAL,
            door_open INTEGER,
            battery_level INTEGER,
            location TEXT,
            rejection_reason TEXT NOT NULL,
            rejected_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pipeline_name TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL,
            input_count INTEGER DEFAULT 0,
            valid_count INTEGER DEFAULT 0,
            rejected_count INTEGER DEFAULT 0,
            error_message TEXT
        )
        """
    )

    connection.commit()

    return connection


def start_pipeline_run(connection):
    started_at = datetime.now().isoformat(
        timespec="seconds"
    )

    cursor = connection.execute(
        """
        INSERT INTO pipeline_runs (
            pipeline_name,
            started_at,
            status
        )
        VALUES (?, ?, ?)
        """,
        (
            "cold_chain_pipeline",
            started_at,
            "RUNNING",
        ),
    )

    connection.commit()

    return cursor.lastrowid


def load_valid_events(connection, events):
    if not events:
        return

    loaded_at = datetime.now().isoformat(
        timespec="seconds"
    )

    rows = []

    for event in events:
        rows.append(
            (
                event["event_id"],
                event["shipment_id"],
                event["device_id"],
                event["event_time"],
                event["event_type"],
                event["temperature"],
                event["humidity"],
                event["door_open"],
                event["battery_level"],
                event["location"],
                loaded_at,
            )
        )

    connection.executemany(
        """
        INSERT INTO cold_chain_events (
            event_id,
            shipment_id,
            device_id,
            event_time,
            event_type,
            temperature,
            humidity,
            door_open,
            battery_level,
            location,
            loaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(event_id)
        DO UPDATE SET
            shipment_id = excluded.shipment_id,
            device_id = excluded.device_id,
            event_time = excluded.event_time,
            event_type = excluded.event_type,
            temperature = excluded.temperature,
            humidity = excluded.humidity,
            door_open = excluded.door_open,
            battery_level = excluded.battery_level,
            location = excluded.location,
            loaded_at = excluded.loaded_at
        """,
        rows,
    )

    connection.commit()

    logging.info(
        "Loaded %d valid events",
        len(rows),
    )


def load_rejected_events(connection, events):
    if not events:
        return

    rejected_at = datetime.now().isoformat(
        timespec="seconds"
    )

    rows = []

    for event in events:
        rows.append(
            (
                event.get("event_id"),
                event.get("shipment_id"),
                event.get("device_id"),
                event.get("event_time"),
                event.get("event_type"),
                event.get("temperature"),
                event.get("humidity"),
                event.get("door_open"),
                event.get("battery_level"),
                event.get("location"),
                event["rejection_reason"],
                rejected_at,
            )
        )

    connection.executemany(
        """
        INSERT INTO rejected_events (
            event_id,
            shipment_id,
            device_id,
            event_time,
            event_type,
            temperature,
            humidity,
            door_open,
            battery_level,
            location,
            rejection_reason,
            rejected_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    connection.commit()

    logging.info(
        "Loaded %d rejected events",
        len(rows),
    )


def create_reports(connection):
    connection.execute(
        """
        DROP VIEW IF EXISTS cold_chain_alerts
        """
    )

    connection.execute(
        f"""
        CREATE VIEW cold_chain_alerts AS
        SELECT
            event_id,
            shipment_id,
            device_id,
            event_time,
            temperature,
            humidity,
            door_open,
            battery_level,
            location,
            CASE
                WHEN temperature < {MIN_TEMPERATURE}
                    THEN 'TOO_COLD'
                WHEN temperature > {MAX_TEMPERATURE}
                    THEN 'TOO_HOT'
                WHEN door_open = 1
                    THEN 'DOOR_OPEN'
                WHEN humidity > {MAX_HUMIDITY}
                    THEN 'HIGH_HUMIDITY'
                WHEN battery_level < {MIN_BATTERY_LEVEL}
                    THEN 'LOW_BATTERY'
                ELSE 'NORMAL'
            END AS alert_type
        FROM cold_chain_events
        WHERE temperature < {MIN_TEMPERATURE}
           OR temperature > {MAX_TEMPERATURE}
           OR door_open = 1
           OR humidity > {MAX_HUMIDITY}
           OR battery_level < {MIN_BATTERY_LEVEL}
        """
    )

    connection.execute(
        """
        DROP VIEW IF EXISTS shipment_summary
        """
    )

    connection.execute(
        f"""
        CREATE VIEW shipment_summary AS
        SELECT
            shipment_id,
            COUNT(*) AS event_count,
            MIN(event_time) AS first_event_time,
            MAX(event_time) AS last_event_time,
            ROUND(AVG(temperature), 2)
                AS average_temperature,
            ROUND(MIN(temperature), 2)
                AS minimum_temperature,
            ROUND(MAX(temperature), 2)
                AS maximum_temperature,
            ROUND(AVG(humidity), 2)
                AS average_humidity,
            SUM(
                CASE
                    WHEN temperature < {MIN_TEMPERATURE}
                      OR temperature > {MAX_TEMPERATURE}
                    THEN 1
                    ELSE 0
                END
            ) AS temperature_violation_count,
            SUM(
                CASE
                    WHEN door_open = 1
                    THEN 1
                    ELSE 0
                END
            ) AS door_open_count,
            CASE
                WHEN SUM(
                    CASE
                        WHEN temperature < {MIN_TEMPERATURE}
                          OR temperature > {MAX_TEMPERATURE}
                        THEN 1
                        ELSE 0
                    END
                ) > 0
                    THEN 'NON_COMPLIANT'
                ELSE 'COMPLIANT'
            END AS shipment_status
        FROM cold_chain_events
        GROUP BY shipment_id
        ORDER BY shipment_id
        """
    )

    connection.execute(
        """
        DROP VIEW IF EXISTS device_health
        """
    )

    connection.execute(
        """
        CREATE VIEW device_health AS
        SELECT
            device_id,
            MAX(event_time) AS last_seen_at,
            MAX(battery_level) AS latest_battery_level,
            CASE
                WHEN MAX(battery_level) < 20
                    THEN 'LOW_BATTERY'
                ELSE 'HEALTHY'
            END AS device_status
        FROM cold_chain_events
        GROUP BY device_id
        """
    )

    connection.commit()


def fetch_rows(connection, query):
    cursor = connection.execute(query)

    column_names = [
        description[0]
        for description in cursor.description
    ]

    rows = cursor.fetchall()

    return [
        dict(zip(column_names, row))
        for row in rows
    ]


def export_json(connection, file_name, query):
    records = fetch_rows(
        connection,
        query,
    )

    output_file = OUTPUT_DIR / file_name

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


def export_reports(connection):
    export_json(
        connection,
        "cold_chain_alerts.json",
        """
        SELECT *
        FROM cold_chain_alerts
        ORDER BY event_time
        """,
    )

    export_json(
        connection,
        "shipment_summary.json",
        """
        SELECT *
        FROM shipment_summary
        """,
    )

    export_json(
        connection,
        "device_health.json",
        """
        SELECT *
        FROM device_health
        """,
    )

    export_json(
        connection,
        "rejected_events.json",
        """
        SELECT *
        FROM rejected_events
        ORDER BY rejection_id
        """,
    )


def complete_pipeline_run(
    connection,
    run_id,
    input_count,
    valid_count,
    rejected_count,
):
    completed_at = datetime.now().isoformat(
        timespec="seconds"
    )

    connection.execute(
        """
        UPDATE pipeline_runs
        SET completed_at = ?,
            status = ?,
            input_count = ?,
            valid_count = ?,
            rejected_count = ?
        WHERE run_id = ?
        """,
        (
            completed_at,
            "SUCCESS",
            input_count,
            valid_count,
            rejected_count,
            run_id,
        ),
    )

    connection.commit()


def fail_pipeline_run(
    connection,
    run_id,
    error_message,
):
    completed_at = datetime.now().isoformat(
        timespec="seconds"
    )

    connection.execute(
        """
        UPDATE pipeline_runs
        SET completed_at = ?,
            status = ?,
            error_message = ?
        WHERE run_id = ?
        """,
        (
            completed_at,
            "FAILED",
            error_message,
            run_id,
        ),
    )

    connection.commit()


def run_pipeline():
    setup_logging()

    connection = None
    run_id = None

    try:
        records = extract_events()

        valid_events, rejected_events = (
            validate_events(records)
        )

        connection = create_database()

        run_id = start_pipeline_run(
            connection
        )

        connection.execute("BEGIN")

        load_valid_events(
            connection,
            valid_events,
        )

        load_rejected_events(
            connection,
            rejected_events,
        )

        create_reports(connection)
        export_reports(connection)

        connection.commit()

        complete_pipeline_run(
            connection,
            run_id,
            len(records),
            len(valid_events),
            len(rejected_events),
        )

        alert_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM cold_chain_alerts
            """
        ).fetchone()[0]

        shipment_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM shipment_summary
            """
        ).fetchone()[0]

        print(
            "Cold-chain pipeline completed "
            "successfully."
        )
        print(f"Input events: {len(records)}")
        print(
            f"Valid events: {len(valid_events)}"
        )
        print(
            f"Rejected events: {len(rejected_events)}"
        )
        print(f"Alerts: {alert_count}")
        print(f"Shipments: {shipment_count}")
        print(f"Database: {DATABASE_FILE}")

    except Exception as error:
        if connection is not None:
            connection.rollback()

            if run_id is not None:
                fail_pipeline_run(
                    connection,
                    run_id,
                    str(error),
                )

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