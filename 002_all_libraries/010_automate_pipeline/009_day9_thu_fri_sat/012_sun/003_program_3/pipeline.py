from pathlib import Path
from datetime import datetime
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "feedback.json"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "stream_feedback.db"
LOG_FILE = OUTPUT_DIR / "stream_feedback_pipeline.log"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

VALID_ISSUES = {
    "Video Quality",
    "Buffering",
    "Audio",
    "UI",
    "Latency",
    "Other",
}


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


def to_integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_feedback():
    logging.info("Extracting feedback")

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("JSON root must be a list")

    logging.info("Extracted %d records", len(records))
    return records


def validate_feedback(records):
    valid_records = []
    rejected_records = []
    seen_ids = set()

    for record in records:
        feedback_id = record.get("feedback_id")
        reason = None

        if not feedback_id:
            reason = "Missing feedback_id"
        elif feedback_id in seen_ids:
            reason = "Duplicate feedback_id"
        elif not record.get("user_id"):
            reason = "Missing user_id"
        elif not record.get("session_id"):
            reason = "Missing session_id"
        elif not is_valid_time(record.get("submitted_at")):
            reason = "Invalid submitted_at"
        elif record.get("issue_type") not in VALID_ISSUES:
            reason = "Invalid issue_type"
        else:
            rating = to_integer(record.get("rating"))
            buffering = to_integer(
                record.get("buffering_seconds")
            )
            latency = to_integer(
                record.get("latency_seconds")
            )

            if rating is None or not 1 <= rating <= 5:
                reason = "Rating must be between 1 and 5"
            elif buffering is None or buffering < 0:
                reason = "Invalid buffering_seconds"
            elif latency is None or latency < 0:
                reason = "Invalid latency_seconds"

        if reason:
            rejected = dict(record)
            rejected["rejection_reason"] = reason
            rejected_records.append(rejected)
            continue

        valid_records.append(
            {
                "feedback_id": feedback_id,
                "user_id": record["user_id"],
                "session_id": record["session_id"],
                "submitted_at": record["submitted_at"],
                "rating": to_integer(record["rating"]),
                "issue_type": record["issue_type"],
                "buffering_seconds": to_integer(
                    record["buffering_seconds"]
                ),
                "latency_seconds": to_integer(
                    record["latency_seconds"]
                ),
                "comments": record.get("comments", ""),
            }
        )

        seen_ids.add(feedback_id)

    logging.info("Valid records: %d", len(valid_records))
    logging.info("Rejected records: %d", len(rejected_records))
    return valid_records, rejected_records


def create_database():
    connection = sqlite3.connect(DATABASE_FILE)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            submitted_at TEXT NOT NULL,
            rating INTEGER NOT NULL,
            issue_type TEXT NOT NULL,
            buffering_seconds INTEGER NOT NULL,
            latency_seconds INTEGER NOT NULL,
            comments TEXT,
            loaded_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS rejected_feedback (
            rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback_id TEXT,
            user_id TEXT,
            session_id TEXT,
            submitted_at TEXT,
            rating INTEGER,
            issue_type TEXT,
            buffering_seconds INTEGER,
            latency_seconds INTEGER,
            comments TEXT,
            rejection_reason TEXT NOT NULL,
            rejected_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    return connection


def load_feedback(connection, valid_records, rejected_records):
    loaded_at = datetime.now().isoformat(timespec="seconds")

    valid_rows = [
        (
            record["feedback_id"],
            record["user_id"],
            record["session_id"],
            record["submitted_at"],
            record["rating"],
            record["issue_type"],
            record["buffering_seconds"],
            record["latency_seconds"],
            record["comments"],
            loaded_at,
        )
        for record in valid_records
    ]

    connection.executemany(
        """
        INSERT INTO feedback (
            feedback_id, user_id, session_id, submitted_at,
            rating, issue_type, buffering_seconds,
            latency_seconds, comments, loaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(feedback_id)
        DO UPDATE SET
            user_id = excluded.user_id,
            session_id = excluded.session_id,
            submitted_at = excluded.submitted_at,
            rating = excluded.rating,
            issue_type = excluded.issue_type,
            buffering_seconds = excluded.buffering_seconds,
            latency_seconds = excluded.latency_seconds,
            comments = excluded.comments,
            loaded_at = excluded.loaded_at
        """,
        valid_rows,
    )

    rejected_rows = [
        (
            record.get("feedback_id"),
            record.get("user_id"),
            record.get("session_id"),
            record.get("submitted_at"),
            record.get("rating"),
            record.get("issue_type"),
            record.get("buffering_seconds"),
            record.get("latency_seconds"),
            record.get("comments"),
            record["rejection_reason"],
            loaded_at,
        )
        for record in rejected_records
    ]

    connection.executemany(
        """
        INSERT INTO rejected_feedback (
            feedback_id, user_id, session_id, submitted_at,
            rating, issue_type, buffering_seconds,
            latency_seconds, comments,
            rejection_reason, rejected_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rejected_rows,
    )

    connection.commit()


def create_feedback_report(connection):
    query = """
        SELECT
            issue_type,
            COUNT(*) AS feedback_count,
            ROUND(AVG(rating), 2) AS average_rating,
            ROUND(AVG(buffering_seconds), 2)
                AS average_buffering_seconds,
            ROUND(AVG(latency_seconds), 2)
                AS average_latency_seconds,
            SUM(
                CASE
                    WHEN rating <= 2 THEN 1
                    ELSE 0
                END
            ) AS negative_feedback_count,
            CASE
                WHEN AVG(rating) >= 4 THEN 'Good'
                WHEN AVG(rating) >= 3 THEN 'Needs Improvement'
                ELSE 'Critical'
            END AS feedback_status
        FROM feedback
        GROUP BY issue_type
        ORDER BY average_rating
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

    output_file = OUTPUT_DIR / "feedback_summary.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    return records


def run_pipeline():
    setup_logging()
    connection = None

    try:
        records = extract_feedback()

        valid_records, rejected_records = validate_feedback(
            records
        )

        connection = create_database()

        connection.execute("BEGIN")

        load_feedback(
            connection,
            valid_records,
            rejected_records,
        )

        report = create_feedback_report(connection)

        connection.commit()

        print("Live-stream feedback pipeline completed.")
        print(f"Input feedback: {len(records)}")
        print(f"Valid feedback: {len(valid_records)}")
        print(f"Rejected feedback: {len(rejected_records)}")
        print(f"Issue categories: {len(report)}")

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