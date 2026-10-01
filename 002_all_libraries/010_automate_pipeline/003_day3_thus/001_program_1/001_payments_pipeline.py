from pathlib import Path
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "payments.json"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "payments.db"
LOG_FILE = OUTPUT_DIR / "payments_pipeline.log"


def setup_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def extract_json():
    logging.info("Starting payment extraction")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(
            "The JSON root must contain a list of payments"
        )

    logging.info(
        "Extracted %d payment records",
        len(records),
    )

    return records


def load_raw_data(records, connection):
    logging.info("Loading raw payments into SQLite")

    connection.execute("DROP TABLE IF EXISTS raw_payments")

    connection.execute(
        """
        CREATE TABLE raw_payments (
            load_id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT,
            order_id TEXT,
            customer_id TEXT,
            payment_date TEXT,
            amount TEXT,
            method TEXT,
            status TEXT,
            order_amount TEXT
        )
        """
    )

    insert_query = """
        INSERT INTO raw_payments (
            payment_id,
            order_id,
            customer_id,
            payment_date,
            amount,
            method,
            status,
            order_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows = []

    for record in records:
        rows.append(
            (
                record.get("payment_id"),
                record.get("order_id"),
                record.get("customer_id"),
                record.get("payment_date"),
                record.get("amount"),
                record.get("method"),
                record.get("status"),
                record.get("order_amount"),
            )
        )

    connection.executemany(insert_query, rows)
    connection.commit()

    logging.info(
        "Loaded %d raw payment records",
        len(rows),
    )


def transform_in_database(connection):
    logging.info("Starting SQL transformations")

    connection.execute("DROP TABLE IF EXISTS clean_payments")

    connection.execute(
        """
        CREATE TABLE clean_payments AS
        WITH typed_payments AS (
            SELECT
                load_id,
                payment_id,
                order_id,
                customer_id,
                payment_date,
                CAST(amount AS REAL) AS amount,
                method,
                status,
                CAST(order_amount AS REAL) AS order_amount
            FROM raw_payments
        ),
        ranked_payments AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY payment_id
                    ORDER BY load_id
                ) AS row_number
            FROM typed_payments
        )
        SELECT
            payment_id,
            order_id,
            customer_id,
            payment_date,
            amount,
            method,
            status,
            order_amount,
            ROUND(amount - order_amount, 2)
                AS reconciliation_difference,
            CASE
                WHEN status <> 'Success'
                    THEN 'Failed Payment'
                WHEN ABS(amount - order_amount) <= 0.01
                    THEN 'Matched'
                ELSE 'Amount Mismatch'
            END AS reconciliation_status
        FROM ranked_payments
        WHERE row_number = 1
          AND payment_id IS NOT NULL
          AND order_id IS NOT NULL
          AND customer_id IS NOT NULL
          AND payment_date GLOB '????-??-??'
          AND amount >= 0
          AND order_amount >= 0
          AND method IN (
              'UPI',
              'Card',
              'Net Banking',
              'Wallet'
          )
          AND status IN (
              'Success',
              'Failed'
          )
        """
    )

    connection.execute("DROP TABLE IF EXISTS rejected_payments")

    connection.execute(
        """
        CREATE TABLE rejected_payments AS
        SELECT
            r.*,
            CASE
                WHEN r.payment_id IS NULL
                    THEN 'Missing payment_id'
                WHEN r.order_id IS NULL
                    THEN 'Missing order_id'
                WHEN r.customer_id IS NULL
                    THEN 'Missing customer_id'
                WHEN r.payment_date NOT GLOB '????-??-??'
                    THEN 'Invalid payment_date'
                WHEN CAST(r.amount AS REAL) < 0
                    THEN 'Amount cannot be negative'
                WHEN CAST(r.order_amount AS REAL) < 0
                    THEN 'Order amount cannot be negative'
                WHEN r.method NOT IN (
                    'UPI',
                    'Card',
                    'Net Banking',
                    'Wallet'
                )
                    THEN 'Invalid payment method'
                WHEN r.status NOT IN (
                    'Success',
                    'Failed'
                )
                    THEN 'Invalid payment status'
                WHEN r.load_id NOT IN (
                    SELECT MIN(load_id)
                    FROM raw_payments
                    GROUP BY payment_id
                )
                    THEN 'Duplicate payment_id'
                ELSE 'Validation failed'
            END AS rejection_reason
        FROM raw_payments AS r
        WHERE r.load_id NOT IN (
            SELECT MIN(load_id)
            FROM raw_payments
            GROUP BY payment_id
        )
        OR r.payment_id IS NULL
        OR r.order_id IS NULL
        OR r.customer_id IS NULL
        OR r.payment_date NOT GLOB '????-??-??'
        OR CAST(r.amount AS REAL) < 0
        OR CAST(r.order_amount AS REAL) < 0
        OR r.method NOT IN (
            'UPI',
            'Card',
            'Net Banking',
            'Wallet'
        )
        OR r.status NOT IN (
            'Success',
            'Failed'
        )
        """
    )

    connection.execute("DROP TABLE IF EXISTS payment_summary")

    connection.execute(
        """
        CREATE TABLE payment_summary AS
        SELECT
            payment_date,
            method,
            COUNT(*) AS payment_count,
            ROUND(
                SUM(
                    CASE
                        WHEN status = 'Success'
                        THEN amount
                        ELSE 0
                    END
                ),
                2
            ) AS successful_amount,
            SUM(
                CASE
                    WHEN status = 'Failed'
                    THEN 1
                    ELSE 0
                END
            ) AS failed_payment_count
        FROM clean_payments
        GROUP BY payment_date, method
        ORDER BY payment_date, method
        """
    )

    connection.execute(
        "DROP TABLE IF EXISTS reconciliation_summary"
    )

    connection.execute(
        """
        CREATE TABLE reconciliation_summary AS
        SELECT
            reconciliation_status,
            COUNT(*) AS payment_count,
            ROUND(SUM(amount), 2) AS total_amount
        FROM clean_payments
        GROUP BY reconciliation_status
        ORDER BY reconciliation_status
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

    result = []

    for row in rows:
        result.append(
            dict(zip(column_names, row))
        )

    return result


def export_json(connection):
    logging.info("Exporting transformed tables")

    output_tables = {
        "clean_payments": "clean_payments.json",
        "rejected_payments": "rejected_payments.json",
        "payment_summary": "payment_summary.json",
        "reconciliation_summary": (
            "reconciliation_summary.json"
        ),
    }

    for table_name, file_name in output_tables.items():
        records = fetch_table(
            connection,
            table_name,
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

        logging.info(
            "Exported %d records to %s",
            len(records),
            output_file,
        )


def verify_pipeline(connection):
    clean_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM clean_payments
        """
    ).fetchone()[0]

    rejected_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM rejected_payments
        """
    ).fetchone()[0]

    matched_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM clean_payments
        WHERE reconciliation_status = 'Matched'
        """
    ).fetchone()[0]

    mismatch_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM clean_payments
        WHERE reconciliation_status = 'Amount Mismatch'
        """
    ).fetchone()[0]

    failed_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM clean_payments
        WHERE reconciliation_status = 'Failed Payment'
        """
    ).fetchone()[0]

    return (
        clean_count,
        rejected_count,
        matched_count,
        mismatch_count,
        failed_count,
    )


def run_pipeline():
    setup_logging()

    connection = None

    try:
        records = extract_json()

        connection = sqlite3.connect(
            DATABASE_FILE
        )

        load_raw_data(
            records,
            connection,
        )

        transform_in_database(
            connection
        )

        export_json(
            connection
        )

        (
            clean_count,
            rejected_count,
            matched_count,
            mismatch_count,
            failed_count,
        ) = verify_pipeline(connection)

        print(
            "Payments ELT pipeline completed successfully."
        )
        print(f"Clean payments: {clean_count}")
        print(f"Rejected payments: {rejected_count}")
        print(f"Matched payments: {matched_count}")
        print(
            f"Amount mismatches: {mismatch_count}"
        )
        print(f"Failed payments: {failed_count}")
        print(f"Database: {DATABASE_FILE}")

    except Exception as error:
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