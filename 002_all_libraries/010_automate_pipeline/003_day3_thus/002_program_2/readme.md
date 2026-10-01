# Enterprise Payment Pipeline

A small batch-processing example for enterprise payment transactions. The pipeline loads transactions from JSON, performs simulated cryptographic verification in parallel, and persists verified records to a local SQLite database using SQLAlchemy.

## Requirements

- Python 3.8 or newer
- Dependencies listed in `requirements.txt`
- AWS credentials available to `boto3` if the default AWS credential lookup requires them

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Run the pipeline from this directory so the relative input and database paths resolve correctly:

```powershell
python .\001_EnterprisePaymentPipeline.py
```

The program reads `payments_batch.json` and creates or updates `payments.db`. Logging reports the verification and database commit steps. If the input file is missing, the program reports that the dataset was not found and exits without processing.

## Input Format

`payments_batch.json` must contain a JSON array of transaction objects. Each transaction requires at least:

```json
{
  "txn_id": "TXN-9081234",
  "amount": 250.5
}
```

The sample file also includes `currency`, `gateway`, and `customer_id`. These extra fields are accepted during processing but are not currently stored in the database.

## Database Output

The pipeline creates a `transactions` table in `payments.db` with these columns:

| Column      | Description                                 |
| ----------- | ------------------------------------------- |
| `txn_id`    | Transaction identifier and primary key      |
| `amount`    | Transaction amount                          |
| `status`    | Set to `VERIFIED` after processing          |
| `timestamp` | UTC processing timestamp in ISO 8601 format |

Existing records with the same `txn_id` are updated through SQLAlchemy's `session.merge()` behavior.

## Implementation Notes

- Signature verification is currently simulated by setting `verified` to `True`; no real cryptographic verification is performed.
- A multiprocessing pool uses the available CPU count for verification.
- The configured S3 bucket name is currently a placeholder and no objects are uploaded to S3.
- The `payments.db` file is generated locally and should not be committed if it is intended to remain runtime data.
