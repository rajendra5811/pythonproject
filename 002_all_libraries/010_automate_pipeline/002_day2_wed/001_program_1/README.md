# Student Order Pipeline

A small Python ETL pipeline that extracts orders from JSON, validates and cleans the data, and writes the transformed orders to a new JSON file.

## Project Structure

```text
.
├── 001_student_pipeline.py
├── requirements.txt
└── data/
    ├── orders.json
    └── clean_orders.json
```

The pipeline also creates `data/pipeline.log` when it runs.

## Requirements

- Python 3.9 or newer
- No external packages are required. The standard library is used throughout the project.

## Run the Pipeline

From the project directory, run:

```bash
python 001_student_pipeline.py
```

The script expects the source file at `data/orders.json` and writes the cleaned output to `data/clean_orders.json`.

## What It Does

1. Extracts a list of orders from `data/orders.json`.
2. Validates required fields, positive numeric amounts, and email addresses.
3. Skips invalid orders and records a warning in the log.
4. Normalizes customer names, cities, email addresses, amounts, and dates.
5. Adds a `processed_at` timestamp to each valid order.
6. Counts orders by city and records the distribution in the log.
7. Saves the transformed orders to `data/clean_orders.json`.

An order must contain `order_id`, `customer`, `email`, `city`, `amount`, and `order_date`. Dates must use the `YYYY-MM-DD` format.

## Sample Result

The included sample data contains three orders. Two valid orders are written to `data/clean_orders.json`; the order with an invalid email address is skipped.

## Logging

Pipeline activity is written to:

```text
data/pipeline.log
```

The log includes extraction counts, skipped records, transformation results, city distribution, and failures.
