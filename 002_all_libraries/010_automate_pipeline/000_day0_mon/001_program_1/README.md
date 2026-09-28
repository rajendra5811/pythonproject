# Order Processing Pipeline

This project contains a small ETL-style Python pipeline that reads order data, validates it, cleans and transforms it, and writes the cleaned output to a JSON file.

## What the pipeline does

- Reads orders from `data/orders.json`
- Validates required fields and basic data quality rules
- Normalizes customer, city, and email values
- Rounds monetary amounts to two decimals
- Standardizes dates
- Writes valid cleaned orders to `data/clean_orders.json`
- Logs pipeline activity to `data/pipeline.log`

## Project structure

- `001_pipeline.py` — main pipeline script
- `data/orders.json` — source input data
- `data/clean_orders.json` — cleaned output data
- `data/pipeline.log` — execution log
- `requirements.txt` — project dependencies (currently empty)

## Requirements

- Python 3.9+
- No external packages are required for this script

## Run the pipeline

From the project folder:

```bash
python 001_pipeline.py
```

If you are using a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python 001_pipeline.py
```

## Expected input format

The input file should be a JSON array of order objects, for example:

```json
[
  {
    "order_id": "A-1001",
    "customer": "  jane smith ",
    "email": "JANE@EXAMPLE.COM",
    "city": "  paris  ",
    "amount": 125.5,
    "order_date": "2024-01-15"
  }
]
```

## Validation rules

Orders are kept only if they include all required fields and pass checks for:

- valid email format
- positive numeric amount
- required keys present
- valid JSON list structure

## Output

The cleaned output is saved as JSON and contains processed records with standardized formatting and a `processed_at` timestamp.
