# Payments ELT Pipeline

A small Python ELT pipeline that loads payment records from JSON into SQLite, validates and transforms them with SQL, and exports clean and summary datasets as JSON.

## Requirements

- Python 3.9 or later
- No third-party packages are required. The pipeline uses only the Python standard library.

## Project Structure

```text
.
|-- 001_payments_pipeline.py
|-- requirements.txt
|-- data/
|   `-- payments.json
`-- output/
    |-- clean_payments.json
    |-- rejected_payments.json
    |-- payment_summary.json
    `-- reconciliation_summary.json
```

The SQLite database (`payments.db`) and pipeline log (`output/payments_pipeline.log`) are generated when the pipeline runs.

## Run the Pipeline

From the project directory, run:

```bash
python 001_payments_pipeline.py
```

The script prints the number of clean, rejected, and matched payments, along with the database path.

## Pipeline Steps

1. **Extract** payment records from `data/payments.json`.
2. **Load** the raw records into the `raw_payments` SQLite table.
3. **Transform** the data with SQL:
   - Cast amounts to numeric values.
   - Keep the first occurrence of each `payment_id`.
   - Validate required IDs, dates, amounts, methods, and statuses.
   - Compare payment amounts with order amounts.
   - Build payment and reconciliation summaries.
4. **Export** SQLite tables to JSON files in `output/`.
5. **Verify** clean, rejected, and matched record counts.

## Validation and Reconciliation

Accepted records must have:

- `payment_id`, `order_id`, and `customer_id`
- A date in `YYYY-MM-DD` format
- Non-negative `amount` and `order_amount`
- A payment method of `UPI`, `Card`, `Net Banking`, or `Wallet`
- A status of `Success` or `Failed`

A successful payment is `Matched` when the payment amount and order amount differ by no more than `0.01`. Other successful payments are marked `Amount Mismatch`, while failed payments are marked `Failed Payment`.

## Output Files

- `clean_payments.json`: validated, de-duplicated payments with reconciliation fields.
- `rejected_payments.json`: records that failed validation, including a `rejection_reason`.
- `payment_summary.json`: payment counts, successful amounts, and failed counts grouped by date and method.
- `reconciliation_summary.json`: payment counts and total amounts grouped by reconciliation status.
- `payments.db`: SQLite database containing the raw and transformed tables.
- `payments_pipeline.log`: execution and error log.
