# Payment Reconciliation Pipeline

A small, repeatable ELT pipeline for turning raw payment events into clean records, rejection details, and reconciliation reports.

> **Pipeline pulse** `JSON -> SQLite staging -> SQL validation -> JSON reports`

## What this project does

The script reads payment records from `data/payments.json`, loads them into a fresh SQLite staging table, applies validation and deduplication rules in SQL, and writes the results to `output/`.

Each run is intentionally reproducible:

- `raw_payments` is rebuilt from the input file.
- The derived SQLite tables are rebuilt from the raw data.
- JSON exports are overwritten with the latest results.
- A run log is written to `output/payments_pipeline.log`.

## Run it

Python 3.9+ is recommended because the script uses the standard library only.

```powershell
python 001_payments_pipeline.py
```

A successful run prints counts for clean, rejected, matched, mismatched, and failed payments, plus the location of `payments.db`.

No third-party packages are required. The entries in `requirements.txt` are all Python standard-library modules used by the script.

## Input contract

`data/payments.json` must contain a JSON array. Each payment can include:

| Field          | Purpose                                   |
| -------------- | ----------------------------------------- |
| `payment_id`   | Unique payment identifier                 |
| `order_id`     | Related order identifier                  |
| `customer_id`  | Customer identifier                       |
| `payment_date` | Date in `YYYY-MM-DD` form                 |
| `amount`       | Amount received                           |
| `method`       | `UPI`, `Card`, `Net Banking`, or `Wallet` |
| `status`       | `Success` or `Failed`                     |
| `order_amount` | Expected order amount                     |

## Validation and reconciliation

A record enters `clean_payments` only when it has:

- All three identifiers: `payment_id`, `order_id`, and `customer_id`
- A date matching `YYYY-MM-DD`
- Non-negative `amount` and `order_amount`
- A supported payment method
- A supported payment status
- The first occurrence of its `payment_id`

Duplicate identifiers and invalid records are retained in `rejected_payments` with a rejection reason. For clean records, reconciliation is calculated as:

```text
reconciliation_difference = amount - order_amount
```

The resulting status is:

- `Matched`: difference is within `0.01`
- `Amount Mismatch`: difference exceeds `0.01`
- `Failed Payment`: payment status is `Failed`

## Generated outputs

| File                                 | Contents                                                |
| ------------------------------------ | ------------------------------------------------------- |
| `output/clean_payments.json`         | Valid, deduplicated payments with reconciliation fields |
| `output/rejected_payments.json`      | Records excluded from the clean dataset and why         |
| `output/payment_summary.json`        | Daily totals by payment method                          |
| `output/reconciliation_summary.json` | Counts and amounts by reconciliation status             |
| `output/payments_pipeline.log`       | Timestamped execution log                               |
| `payments.db`                        | SQLite database containing raw and derived tables       |

## SQLite tables

The database contains:

- `raw_payments`: source records loaded from JSON
- `clean_payments`: validated and deduplicated records
- `rejected_payments`: excluded records with rejection reasons
- `payment_summary`: daily method-level aggregates
- `reconciliation_summary`: reconciliation-level aggregates

## Troubleshooting

- **Input file not found:** confirm `data/payments.json` exists beside the script.
- **JSON root error:** ensure the file starts with an array, not an object.
- **Unexpected results:** inspect `output/rejected_payments.json` and `output/payments_pipeline.log`.
- **Stale artifacts:** rerun the script; its tables and report files are rebuilt each time.
