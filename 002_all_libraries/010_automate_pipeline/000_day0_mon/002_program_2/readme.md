# Orders Data Pipeline

A small ETL pipeline that extracts order data from CSV, validates and cleans it, creates daily sales summaries, and loads the results into CSV files and SQLite.

## Project structure

```text
002_program_2/
|-- 001_orders_pipeline.py
|-- requirements.txt
|-- readme.md
|-- orders.db                  # Created when the pipeline runs
|-- BASE_DIR/
|   `-- data/
|       |-- orders.csv         # Input data
|       `-- 002_sql_db.py      # SQL query example
`-- output/                    # Created/populated by the pipeline
    |-- clean_orders.csv
    |-- rejected_orders.csv
    |-- daily_sales_summary.csv
    `-- orders_pipeline.log
```

## Requirements

- Python 3.9 or newer
- pandas

Install the dependency with:

```powershell
python -m pip install -r requirements.txt
```

## Run the pipeline

Run this command from the project root:

```powershell
python 001_orders_pipeline.py
```

The pipeline reads `BASE_DIR\data\orders.csv`, validates the required columns and values, removes duplicate `order_id` values, and creates:

- `output/clean_orders.csv`
- `output/rejected_orders.csv`
- `output/daily_sales_summary.csv`
- `orders.db`
- `output/orders_pipeline.log`

## Query the SQLite database

After the pipeline has completed, run:

```powershell
python BASE_DIR\data\002_sql_db.py
```

This prints completed orders grouped by order date, including order counts and revenue.

## Validation rules

Records are rejected when they have:

- An invalid or missing `order_date`
- A non-positive or invalid `quantity`
- A negative or invalid `unit_price`
- A status other than `Completed` or `Cancelled`
- Missing `order_id`, `customer_id`, or `product_id`
- A duplicate `order_id`
