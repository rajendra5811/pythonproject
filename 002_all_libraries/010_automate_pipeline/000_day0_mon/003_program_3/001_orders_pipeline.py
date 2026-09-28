from pathlib import Path
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "orders.json"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "orders.db"
LOG_FILE = OUTPUT_DIR / "orders_pipeline.log"


def setup_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def extract_json():
    logging.info("Starting extraction from JSON")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("JSON root must contain a list of orders")

    logging.info("Extracted %d records", len(records))

    return records


def load_raw_data(records, connection):
    logging.info("Loading raw records into SQLite")

    connection.execute("DROP TABLE IF EXISTS raw_orders")

    connection.execute(
        """
        CREATE TABLE raw_orders (
            load_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            customer_id TEXT,
            order_date TEXT,
            product_id TEXT,
            quantity TEXT,
            unit_price TEXT,
            status TEXT
        )
        """
    )

    insert_query = """
        INSERT INTO raw_orders (
            order_id,
            customer_id,
            order_date,
            product_id,
            quantity,
            unit_price,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    rows = [
        (
            record.get("order_id"),
            record.get("customer_id"),
            record.get("order_date"),
            record.get("product_id"),
            record.get("quantity"),
            record.get("unit_price"),
            record.get("status"),
        )
        for record in records
    ]

    connection.executemany(insert_query, rows)
    connection.commit()

    logging.info("Loaded %d raw records", len(rows))


def transform_in_database(connection):
    logging.info("Starting SQL transformations")

    connection.execute("DROP TABLE IF EXISTS clean_orders")

    connection.execute(
        """
        CREATE TABLE clean_orders AS
        WITH typed_orders AS (
            SELECT
                load_id,
                order_id,
                customer_id,
                order_date,
                product_id,
                CAST(quantity AS INTEGER) AS quantity,
                CAST(unit_price AS REAL) AS unit_price,
                status
            FROM raw_orders
        ),
        ranked_orders AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY order_id
                    ORDER BY load_id
                ) AS row_number
            FROM typed_orders
        )
        SELECT
            order_id,
            customer_id,
            order_date,
            product_id,
            quantity,
            unit_price,
            quantity * unit_price AS total_amount,
            status
        FROM ranked_orders
        WHERE row_number = 1
          AND order_id IS NOT NULL
          AND customer_id IS NOT NULL
          AND product_id IS NOT NULL
          AND order_date GLOB '????-??-??'
          AND quantity > 0
          AND unit_price >= 0
          AND status IN ('Completed', 'Cancelled')
        """
    )

    connection.execute("DROP TABLE IF EXISTS rejected_orders")

    connection.execute(
        """
        CREATE TABLE rejected_orders AS
        SELECT
            r.*,
            CASE
                WHEN r.order_id IS NULL
                    THEN 'Missing order_id'
                WHEN r.customer_id IS NULL
                    THEN 'Missing customer_id'
                WHEN r.product_id IS NULL
                    THEN 'Missing product_id'
                WHEN r.order_date NOT GLOB '????-??-??'
                    THEN 'Invalid order_date'
                WHEN CAST(r.quantity AS INTEGER) <= 0
                    THEN 'Invalid quantity'
                WHEN CAST(r.unit_price AS REAL) < 0
                    THEN 'Invalid unit_price'
                WHEN r.status NOT IN ('Completed', 'Cancelled')
                    THEN 'Invalid status'
                WHEN r.load_id NOT IN (
                    SELECT MIN(load_id)
                    FROM raw_orders
                    GROUP BY order_id
                )
                    THEN 'Duplicate order_id'
                ELSE 'Validation failed'
            END AS rejection_reason
        FROM raw_orders AS r
        WHERE r.load_id NOT IN (
            SELECT c.load_id
            FROM (
                SELECT MIN(load_id) AS load_id
                FROM raw_orders
                GROUP BY order_id
            ) AS c
        )
        OR r.order_id IS NULL
        OR r.customer_id IS NULL
        OR r.product_id IS NULL
        OR r.order_date NOT GLOB '????-??-??'
        OR CAST(r.quantity AS INTEGER) <= 0
        OR CAST(r.unit_price AS REAL) < 0
        OR r.status NOT IN ('Completed', 'Cancelled')
        """
    )

    connection.execute("DROP TABLE IF EXISTS daily_sales_summary")

    connection.execute(
        """
        CREATE TABLE daily_sales_summary AS
        SELECT
            order_date,
            COUNT(DISTINCT order_id) AS total_orders,
            SUM(quantity) AS total_quantity,
            ROUND(SUM(total_amount), 2) AS total_revenue
        FROM clean_orders
        WHERE status = 'Completed'
        GROUP BY order_date
        ORDER BY order_date
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
    logging.info("Exporting transformed data")

    tables = {
        "clean_orders": "clean_orders.json",
        "rejected_orders": "rejected_orders.json",
        "daily_sales_summary": "daily_sales_summary.json",
    }

    for table_name, file_name in tables.items():
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


def run_pipeline():
    setup_logging()
    connection = None

    try:
        records = extract_json()

        connection = sqlite3.connect(DATABASE_FILE)

        load_raw_data(records, connection)
        transform_in_database(connection)
        export_json(connection)

        clean_count = connection.execute(
            "SELECT COUNT(*) FROM clean_orders"
        ).fetchone()[0]

        rejected_count = connection.execute(
            "SELECT COUNT(*) FROM rejected_orders"
        ).fetchone()[0]

        print("Orders ELT pipeline completed successfully.")
        print(f"Clean records: {clean_count}")
        print(f"Rejected records: {rejected_count}")
        print(f"Database: {DATABASE_FILE}")

    except Exception as error:
        logging.exception("Pipeline failed: %s", error)
        print(f"Pipeline failed: {error}")

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    run_pipeline()