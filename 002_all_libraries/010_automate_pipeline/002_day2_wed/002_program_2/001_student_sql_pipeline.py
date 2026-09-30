from pathlib import Path
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "students.json"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "students.db"
LOG_FILE = OUTPUT_DIR / "students_pipeline.log"


def setup_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def extract_json():
    logging.info("Starting extraction")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("JSON root must contain a list")

    logging.info("Extracted %d records", len(records))

    return records


def load_raw_data(records, connection):
    logging.info("Loading raw records into SQLite")

    connection.execute("DROP TABLE IF EXISTS raw_students")

    connection.execute(
        """
        CREATE TABLE raw_students (
            load_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            name TEXT,
            department TEXT,
            marks TEXT,
            attendance TEXT,
            exam_date TEXT
        )
        """
    )

    insert_query = """
        INSERT INTO raw_students (
            student_id,
            name,
            department,
            marks,
            attendance,
            exam_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    rows = [
        (
            record.get("student_id"),
            record.get("name"),
            record.get("department"),
            record.get("marks"),
            record.get("attendance"),
            record.get("exam_date"),
        )
        for record in records
    ]

    connection.executemany(insert_query, rows)
    connection.commit()

    logging.info("Loaded %d raw records", len(rows))


def transform_in_database(connection):
    logging.info("Starting SQL transformations")

    connection.execute("DROP TABLE IF EXISTS clean_students")

    connection.execute(
        """
        CREATE TABLE clean_students AS
        WITH typed_students AS (
            SELECT
                load_id,
                student_id,
                TRIM(name) AS name,
                TRIM(department) AS department,
                CAST(marks AS INTEGER) AS marks,
                CAST(attendance AS INTEGER) AS attendance,
                exam_date
            FROM raw_students
        ),
        ranked_students AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY student_id
                    ORDER BY load_id
                ) AS row_number
            FROM typed_students
        )
        SELECT
            student_id,
            name,
            department,
            marks,
            attendance,
            exam_date,
            CASE
                WHEN marks >= 90 THEN 'A'
                WHEN marks >= 75 THEN 'B'
                WHEN marks >= 60 THEN 'C'
                WHEN marks >= 40 THEN 'D'
                ELSE 'F'
            END AS grade,
            CASE
                WHEN attendance >= 75 THEN 'Eligible'
                ELSE 'Not Eligible'
            END AS exam_eligibility
        FROM ranked_students
        WHERE row_number = 1
          AND student_id IS NOT NULL
          AND name IS NOT NULL
          AND name <> ''
          AND department IS NOT NULL
          AND department <> ''
          AND exam_date GLOB '????-??-??'
          AND marks BETWEEN 0 AND 100
          AND attendance BETWEEN 0 AND 100
        """
    )

    connection.execute("DROP TABLE IF EXISTS rejected_students")

    connection.execute(
        """
        CREATE TABLE rejected_students AS
        SELECT
            r.*,
            CASE
                WHEN r.student_id IS NULL
                    THEN 'Missing student_id'
                WHEN r.name IS NULL OR TRIM(r.name) = ''
                    THEN 'Missing name'
                WHEN r.department IS NULL
                     OR TRIM(r.department) = ''
                    THEN 'Missing department'
                WHEN r.exam_date NOT GLOB '????-??-??'
                    THEN 'Invalid exam_date'
                WHEN CAST(r.marks AS INTEGER) NOT BETWEEN 0 AND 100
                    THEN 'Marks must be between 0 and 100'
                WHEN CAST(r.attendance AS INTEGER) NOT BETWEEN 0 AND 100
                    THEN 'Attendance must be between 0 and 100'
                WHEN r.load_id NOT IN (
                    SELECT MIN(load_id)
                    FROM raw_students
                    GROUP BY student_id
                )
                    THEN 'Duplicate student_id'
                ELSE 'Validation failed'
            END AS rejection_reason
        FROM raw_students AS r
        WHERE r.load_id NOT IN (
            SELECT MIN(load_id)
            FROM raw_students
            GROUP BY student_id
        )
        OR r.student_id IS NULL
        OR r.name IS NULL
        OR TRIM(r.name) = ''
        OR r.department IS NULL
        OR TRIM(r.department) = ''
        OR r.exam_date NOT GLOB '????-??-??'
        OR CAST(r.marks AS INTEGER) NOT BETWEEN 0 AND 100
        OR CAST(r.attendance AS INTEGER) NOT BETWEEN 0 AND 100
        """
    )

    connection.execute("DROP TABLE IF EXISTS department_summary")

    connection.execute(
        """
        CREATE TABLE department_summary AS
        SELECT
            department,
            COUNT(*) AS student_count,
            ROUND(AVG(marks), 2) AS average_marks,
            MAX(marks) AS highest_marks,
            MIN(marks) AS lowest_marks,
            SUM(
                CASE
                    WHEN exam_eligibility = 'Eligible'
                    THEN 1
                    ELSE 0
                END
            ) AS eligible_students
        FROM clean_students
        GROUP BY department
        ORDER BY department
        """
    )

    connection.commit()

    logging.info("SQL transformations completed")


def fetch_table(connection, table_name):
    cursor = connection.execute(
        f"SELECT * FROM {table_name}"
    )

    column_names = [
        description[0]
        for description in cursor.description
    ]

    rows = cursor.fetchall()

    return [
        dict(zip(column_names, row))
        for row in rows
    ]


def export_json(connection):
    output_tables = {
        "clean_students": "clean_students.json",
        "rejected_students": "rejected_students.json",
        "department_summary": "department_summary.json",
    }

    for table_name, file_name in output_tables.items():
        records = fetch_table(connection, table_name)
        output_file = OUTPUT_DIR / file_name

        with output_file.open("w", encoding="utf-8") as file:
            json.dump(
                records,
                file,
                indent=4,
                default=str,
            )

        logging.info(
            "Exported %d records to %s",
            len(records),
            output_file,
        )


def verify_pipeline(connection):
    clean_count = connection.execute(
        "SELECT COUNT(*) FROM clean_students"
    ).fetchone()[0]

    rejected_count = connection.execute(
        "SELECT COUNT(*) FROM rejected_students"
    ).fetchone()[0]

    department_count = connection.execute(
        "SELECT COUNT(*) FROM department_summary"
    ).fetchone()[0]

    return clean_count, rejected_count, department_count


def run_pipeline():
    setup_logging()
    connection = None

    try:
        records = extract_json()

        connection = sqlite3.connect(DATABASE_FILE)

        load_raw_data(records, connection)
        transform_in_database(connection)
        export_json(connection)

        clean_count, rejected_count, department_count = (
            verify_pipeline(connection)
        )

        print("Students ELT pipeline completed successfully.")
        print(f"Clean students: {clean_count}")
        print(f"Rejected students: {rejected_count}")
        print(f"Departments summarized: {department_count}")
        print(f"Database: {DATABASE_FILE}")

    except Exception as error:
        logging.exception("Pipeline failed: %s", error)
        print(f"Pipeline failed: {error}")

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    run_pipeline()