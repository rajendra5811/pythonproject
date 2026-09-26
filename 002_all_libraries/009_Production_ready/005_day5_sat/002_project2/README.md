# E-commerce Order Pipeline

A small Python ETL pipeline for loading e-commerce orders from JSON, cleaning and enriching them, validating records, removing duplicate order IDs, and writing the processed orders to JSON.

## Pipeline Flow

1. Load orders from `data/orders.json`.
2. Normalize customer names and email addresses.
3. Calculate shipping, tax, and order totals.
4. Add a processing timestamp.
5. Keep only valid orders.
6. Remove duplicate orders by `order_id`.
7. Save the result to `output/orders.json`.

## Requirements

- Python 3.9 or newer
- The packages imported by the script must be available in the active environment. The current `requirements.txt` is empty; `boto3` and `httpx` are imported by the script but are not currently used by the pipeline logic.

Create and activate a virtual environment, then install the project requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Input

Create `data/orders.json` as a JSON array. Each order should contain at least:

```json
[
  {
    "order_id": "ORD-1001",
    "customer_name": "  Ada Lovelace  ",
    "email": "ADA@example.com",
    "quantity": 2,
    "unit_price": 125.5
  }
]
```

An order is considered valid when it has an `order_id` and `email`, its `quantity` is greater than zero, and its `unit_price` is not negative.

## Run

From the project directory, run:

```powershell
python 001_ecommerce_pipeline.py
```

The processed orders are written to `output/orders.json`. The script also creates a `logs/` directory and emits start/completion messages through Python logging.

## Calculations

- Shipping costs 50 per package.
- Each package contains up to 5 items.
- Tax is calculated at 18% of the subtotal.
- Total is `subtotal + tax + shipping`, rounded to two decimal places.

## Project Structure

```text
.
|-- 001_ecommerce_pipeline.py
|-- requirements.txt
|-- data/
|   `-- orders.json       # Input data, created by the user
|-- output/
|   `-- orders.json       # Generated output
`-- logs/                 # Created when the pipeline starts
```

## Notes

The input file is required before running the pipeline. The script currently uses fixed relative paths, so run it from the project directory. Dependency declarations should be updated in `requirements.txt` if the imported third-party packages remain part of the project.
