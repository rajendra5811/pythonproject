from pathlib import Path
import json
import logging
import sqlite3


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "banking_transactions.json"
)

OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "banking.db"
LOG_FILE = OUTPUT_DIR / "banking_pipeline.log"

VALID_TRANSACTION_TYPES = (
    "Deposit",
    "Withdrawal",
)


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


def extract_json():
    logging.info("Starting banking data extraction")

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
        "Extracted %d transaction records",
        len(records),
    )

    return records


def load_raw_data(records, connection):
    logging.info(
        "Loading raw banking data into SQLite"
    )

    connection.execute(
        "DROP TABLE IF EXISTS raw_transactions"
    )

    connection.execute(
        """
        CREATE TABLE raw_transactions (
            load_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            account_id TEXT,
            transaction_date TEXT,
            transaction_type TEXT,
            amount TEXT,
            balance TEXT,
            location TEXT
        )
        """
    )

    insert_query = """
        INSERT INTO raw_transactions (
            transaction_id,
            account_id,
            transaction_date,
            transaction_type,
            amount,
            balance,
            location
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    rows = []

    for record in records:
        rows.append(
            (
                record.get("transaction_id"),
                record.get("account_id"),
                record.get("transaction_date"),
                record.get("transaction_type"),
                record.get("amount"),
                record.get("balance"),
                record.get("location"),
            )
        )

    connection.executemany(
        insert_query,
        rows,
    )

    connection.commit()

    logging.info(
        "Loaded %d raw transactions",
        len(rows),
    )


def transform_in_database(connection):
    logging.info(
        "Starting SQL transformations"
    )

    connection.execute(
        "DROP TABLE IF EXISTS clean_transactions"
    )

    connection.execute(
        """
        CREATE TABLE clean_transactions AS
        WITH typed_transactions AS (
            SELECT
                load_id,
                transaction_id,
                account_id,
                transaction_date,
                transaction_type,
                CAST(amount AS REAL) AS amount,
                CAST(balance AS REAL) AS balance,
                location
            FROM raw_transactions
        ),
        ranked_transactions AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY transaction_id
                    ORDER BY load_id
                ) AS duplicate_number
            FROM typed_transactions
        ),
        transaction_analysis AS (
            SELECT
                transaction_id,
                account_id,
                transaction_date,
                transaction_type,
                amount,
                balance,
                location,
                LAG(balance) OVER (
                    PARTITION BY account_id
                    ORDER BY transaction_date, load_id
                ) AS previous_balance,
                LAG(transaction_date) OVER (
                    PARTITION BY account_id
                    ORDER BY transaction_date, load_id
                ) AS previous_transaction_date
            FROM ranked_transactions
            WHERE duplicate_number = 1
        )
        SELECT
            transaction_id,
            account_id,
            transaction_date,
            transaction_type,
            amount,
            balance,
            location,
            previous_balance,
            previous_transaction_date,
            ROUND(
                balance - COALESCE(previous_balance, 0),
                2
            ) AS balance_change,
            CASE
                WHEN transaction_type = 'Withdrawal'
                    AND amount > 50000
                    THEN 'High Value Withdrawal'
                WHEN transaction_type = 'Withdrawal'
                    AND location IN (
                        SELECT location
                        FROM raw_transactions
                        GROUP BY location
                        HAVING COUNT(*) > 1
                    )
                    THEN 'Review Location'
                ELSE 'Normal'
            END AS transaction_flag
        FROM transaction_analysis
        """
    )

    connection.execute(
        "DROP TABLE IF EXISTS rejected_transactions"
    )

    connection.execute(
        """
        CREATE TABLE rejected_transactions AS
        SELECT
            r.*,
            CASE
                WHEN r.transaction_id IS NULL
                    THEN 'Missing transaction_id'
                WHEN r.account_id IS NULL
                    THEN 'Missing account_id'
                WHEN r.transaction_date NOT GLOB
                    '????-??-?? ??:??:??'
                    THEN 'Invalid transaction_date'
                WHEN r.transaction_type NOT IN (
                    'Deposit',
                    'Withdrawal'
                )
                    THEN 'Invalid transaction_type'
                WHEN CAST(r.amount AS REAL) <= 0
                    THEN 'Amount must be greater than zero'
                WHEN CAST(r.balance AS REAL) < 0
                    THEN 'Balance cannot be negative'
                WHEN r.location IS NULL
                    OR TRIM(r.location) = ''
                    THEN 'Missing location'
                WHEN r.load_id NOT IN (
                    SELECT MIN(load_id)
                    FROM raw_transactions
                    GROUP BY transaction_id
                )
                    THEN 'Duplicate transaction_id'
                ELSE 'Validation failed'
            END AS rejection_reason
        FROM raw_transactions AS r
        WHERE r.load_id NOT IN (
            SELECT MIN(load_id)
            FROM raw_transactions
            GROUP BY transaction_id
        )
        OR r.transaction_id IS NULL
        OR r.account_id IS NULL
        OR r.transaction_date NOT GLOB
            '????-??-?? ??:??:??'
        OR r.transaction_type NOT IN (
            'Deposit',
            'Withdrawal'
        )
        OR CAST(r.amount AS REAL) <= 0
        OR CAST(r.balance AS REAL) < 0
        OR r.location IS NULL
        OR TRIM(r.location) = ''
        """
    )

    connection.execute(
        "DROP TABLE IF EXISTS account_summary"
    )

    connection.execute(
        """
        CREATE TABLE account_summary AS
        SELECT
            account_id,
            COUNT(*) AS transaction_count,
            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'Deposit'
                        THEN amount
                        ELSE 0
                    END
                ),
                2
            ) AS total_deposits,
            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'Withdrawal'
                        THEN amount
                        ELSE 0
                    END
                ),
                2
            ) AS total_withdrawals,
            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'Deposit'
                        THEN amount
                        WHEN transaction_type = 'Withdrawal'
                        THEN -amount
                        ELSE 0
                    END
                ),
                2
            ) AS net_transaction_amount,
            MAX(balance) AS latest_recorded_balance
        FROM clean_transactions
        GROUP BY account_id
        ORDER BY account_id
        """
    )

    connection.execute(
        "DROP TABLE IF EXISTS monthly_summary"
    )

    connection.execute(
        """
        CREATE TABLE monthly_summary AS
        SELECT
            SUBSTR(transaction_date, 1, 7)
                AS transaction_month,
            COUNT(*) AS transaction_count,
            COUNT(DISTINCT account_id)
                AS active_accounts,
            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'Deposit'
                        THEN amount
                        ELSE 0
                    END
                ),
                2
            ) AS total_deposits,
            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'Withdrawal'
                        THEN amount
                        ELSE 0
                    END
                ),
                2
            ) AS total_withdrawals
        FROM clean_transactions
        GROUP BY SUBSTR(transaction_date, 1, 7)
        ORDER BY transaction_month
        """
    )

    connection.execute(
        "DROP TABLE IF EXISTS fraud_alerts"
    )

    connection.execute(
        """
        CREATE TABLE fraud_alerts AS
        SELECT
            transaction_id,
            account_id,
            transaction_date,
            transaction_type,
            amount,
            balance,
            location,
            transaction_flag,
            CASE
                WHEN transaction_type = 'Withdrawal'
                     AND amount > 50000
                    THEN 'Large withdrawal'
                WHEN transaction_type = 'Withdrawal'
                     AND previous_transaction_date IS NOT NULL
                     AND (
                         strftime(
                             '%s',
                             transaction_date
                         )
                         -
                         strftime(
                             '%s',
                             previous_transaction_date
                         )
                     ) <= 600
                    THEN 'Rapid consecutive transaction'
                WHEN transaction_type = 'Withdrawal'
                     AND amount > balance
                    THEN 'Withdrawal exceeds balance'
                ELSE 'Review required'
            END AS alert_reason
        FROM clean_transactions
        WHERE (
            transaction_type = 'Withdrawal'
            AND amount > 50000
        )
        OR (
            transaction_type = 'Withdrawal'
            AND previous_transaction_date IS NOT NULL
            AND (
                strftime(
                    '%s',
                    transaction_date
                )
                -
                strftime(
                    '%s',
                    previous_transaction_date
                )
            ) <= 600
        )
        OR (
            transaction_type = 'Withdrawal'
            AND amount > balance
        )
        """
    )

    connection.commit()

    logging.info(
        "SQL transformations completed"
    )


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
    logging.info(
        "Exporting banking pipeline results"
    )

    output_tables = {
        "clean_transactions": (
            "clean_transactions.json"
        ),
        "rejected_transactions": (
            "rejected_transactions.json"
        ),
        "account_summary": (
            "account_summary.json"
        ),
        "monthly_summary": (
            "monthly_summary.json"
        ),
        "fraud_alerts": (
            "fraud_alerts.json"
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
        FROM clean_transactions
        """
    ).fetchone()[0]

    rejected_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM rejected_transactions
        """
    ).fetchone()[0]

    account_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM account_summary
        """
    ).fetchone()[0]

    fraud_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fraud_alerts
        """
    ).fetchone()[0]

    return (
        clean_count,
        rejected_count,
        account_count,
        fraud_count,
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
            account_count,
            fraud_count,
        ) = verify_pipeline(connection)

        print(
            "Banking ELT pipeline completed "
            "successfully."
        )
        print(
            f"Clean transactions: {clean_count}"
        )
        print(
            f"Rejected transactions: {rejected_count}"
        )
        print(
            f"Account summaries: {account_count}"
        )
        print(
            f"Fraud alerts: {fraud_count}"
        )
        print(
            f"Database: {DATABASE_FILE}"
        )

    except Exception as error:
        logging.exception(
            "Pipeline failed: %s",
            error,
        )
        print(
            f"Pipeline failed: {error}"
        )

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    run_pipeline()