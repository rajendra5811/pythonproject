from pathlib import Path
import logging
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "orders.csv"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "orders.db"
LOG_FILE = OUTPUT_DIR / "orders_pipeline.log"

REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_date",
    "product_id",
    "quantity",
    "unit_price",
    "status",
]

VALID_STATUSES = {"Completed", "Cancelled"}


def setup_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def extract():
    logging.info("Starting extraction")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    logging.info("Extracted %d rows", len(df))
    return df


def validate_and_clean(df):
    logging.info("Starting validation")

    data = df.copy()
    rejected_records = []

    data["order_date"] = pd.to_datetime(
        data["order_date"],
        errors="coerce",
    )

    data["quantity"] = pd.to_numeric(
        data["quantity"],
        errors="coerce",
    )

    data["unit_price"] = pd.to_numeric(
        data["unit_price"],
        errors="coerce",
    )

    invalid_date = data["order_date"].isna()
    invalid_quantity = data["quantity"].isna() | (data["quantity"] <= 0)
    invalid_price = data["unit_price"].isna() | (data["unit_price"] < 0)
    invalid_status = ~data["status"].isin(VALID_STATUSES)
    missing_required = data[
        ["order_id", "customer_id", "product_id"]
    ].isna().any(axis=1)

    invalid_rows = (
        invalid_date
        | invalid_quantity
        | invalid_price
        | invalid_status
        | missing_required
    )

    rejected = data[invalid_rows].copy()

    if not rejected.empty:
        rejected["rejection_reason"] = "Validation failed"
        rejected_records.append(rejected)

    clean_data = data[~invalid_rows].copy()

    duplicate_rows = clean_data[
        clean_data.duplicated(
            subset=["order_id"],
            keep="first",
        )
    ].copy()

    if not duplicate_rows.empty:
        duplicate_rows["rejection_reason"] = "Duplicate order_id"
        rejected_records.append(duplicate_rows)

    clean_data = clean_data.drop_duplicates(
        subset=["order_id"],
        keep="first",
    )

    if rejected_records:
        rejected_data = pd.concat(
            rejected_records,
            ignore_index=True,
        )
    else:
        rejected_data = pd.DataFrame()

    logging.info("Clean rows: %d", len(clean_data))
    logging.info("Rejected rows: %d", len(rejected_data))

    return clean_data, rejected_data


def transform(df):
    logging.info("Starting transformation")

    data = df.copy()

    data["total_amount"] = (
        data["quantity"] * data["unit_price"]
    )

    data["order_date"] = data["order_date"].dt.strftime(
        "%Y-%m-%d"
    )

    data = data[
        [
            "order_id",
            "customer_id",
            "order_date",
            "product_id",
            "quantity",
            "unit_price",
            "total_amount",
            "status",
        ]
    ]

    daily_summary = (
        data[data["status"] == "Completed"]
        .groupby("order_date", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
        )
        .sort_values("order_date")
    )

    logging.info("Transformation completed")

    return data, daily_summary


def load(clean_data, rejected_data, daily_summary):
    logging.info("Starting load")

    OUTPUT_DIR.mkdir(exist_ok=True)

    clean_data.to_csv(
        OUTPUT_DIR / "clean_orders.csv",
        index=False,
    )

    rejected_data.to_csv(
        OUTPUT_DIR / "rejected_orders.csv",
        index=False,
    )

    daily_summary.to_csv(
        OUTPUT_DIR / "daily_sales_summary.csv",
        index=False,
    )

    with sqlite3.connect(DATABASE_FILE) as connection:
        clean_data.to_sql(
            "orders",
            connection,
            if_exists="replace",
            index=False,
        )

        daily_summary.to_sql(
            "daily_sales_summary",
            connection,
            if_exists="replace",
            index=False,
        )

    logging.info("Data loaded into CSV files and SQLite")
    logging.info("Pipeline completed successfully")


def run_pipeline():
    try:
        setup_logging()

        raw_data = extract()

        clean_data, rejected_data = validate_and_clean(
            raw_data
        )

        transformed_data, daily_summary = transform(
            clean_data
        )

        load(
            transformed_data,
            rejected_data,
            daily_summary,
        )

        print("Orders pipeline completed successfully.")
        print(f"Clean records: {len(transformed_data)}")
        print(f"Rejected records: {len(rejected_data)}")
        print(f"Database: {DATABASE_FILE}")

    except Exception as error:
        logging.exception("Pipeline failed: %s", error)
        print(f"Pipeline failed: {error}")


if __name__ == "__main__":
    run_pipeline()