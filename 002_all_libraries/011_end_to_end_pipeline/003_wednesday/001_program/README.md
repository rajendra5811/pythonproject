# Wildlife Telemetry Pipeline

A small Python pipeline for validating wildlife-collar telemetry, calculating
stress indicators, classifying animal status, and persisting processed records
to SQLite with SQLAlchemy.

## Features

- Validates collar IDs using the `WLD-####` format.
- Calculates a stress index from movement speed.
- Classifies records as `NORMAL_HABITAT` or `POACHING_ALERT`.
- Reports batch status counts and average speed.
- Persists valid telemetry to the `wildlife_collars` SQLite table.
- Performs a basic system and subprocess audit before processing.

## Requirements

- Python 3.9 or newer
- Packages listed in [`requirements.txt`](requirements.txt)

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## Run

```powershell
py wildlife_pipeline.py
```

The pipeline creates or updates `wildlife_core.db` in the working directory
and creates a `wildlife_vault` directory for local pipeline artifacts.

## Data handling

Records with invalid collar IDs are skipped and logged. Valid records are
merged into the database by `collar_id`, so rerunning the pipeline updates
existing collar records rather than creating duplicates.
