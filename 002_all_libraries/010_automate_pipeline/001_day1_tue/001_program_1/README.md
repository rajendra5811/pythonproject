# Log Pipeline

A simple Python pipeline that scans incoming `.log` files, counts `ERROR` entries, logs malformed lines, and moves each processed file into an archive folder.

## Project structure

- `001_log_Pipeline.py` — main pipeline script
- `simple_logs/incoming` — place incoming log files here
- `simple_logs/archive` — processed files are moved here

## How it works

1. The script creates the `simple_logs/incoming` and `simple_logs/archive` directories if they do not exist.
2. It looks for all `*.log` files in the incoming folder.
3. Each line is checked against a simple log format:
   - timestamp
   - service name in brackets
   - log level
   - message text
4. If a line matches and its level is `ERROR`, the error count increases.
5. Malformed lines are skipped and logged as warnings.
6. After processing, the file is moved to the archive directory.

## Run the pipeline

```bash
python 001_log_Pipeline.py
```

## Libraries used and their purpose

- `pathlib` — used to safely create and manage the working directories (`simple_logs/incoming` and `simple_logs/archive`) in a clean, cross-platform way.
- `logging` — used to print pipeline status, warnings, and error messages while the script runs.
- `re` (regular expressions) — used to validate whether each log line follows the expected format before counting it as an error.
- `shutil` — used to move processed log files from the incoming folder into the archive folder after they are handled.
- `datetime` — imported for date/time handling and compatibility with log processing scenarios, even though this basic example mainly uses it for standard Python setup.

## Example log format

```text
2026-03-30 10:00:00 [AUTH] ERROR: Failed login
2026-03-30 10:05:12 [API] INFO: Request processed successfully
```

## Notes

- This is a basic example designed for learning and automation practice.
- It uses a simple regex to validate log lines and does not yet include database storage, dashboards, or advanced error handling.
