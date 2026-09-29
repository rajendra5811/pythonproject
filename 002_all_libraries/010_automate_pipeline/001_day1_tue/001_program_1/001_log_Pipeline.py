"""Scenario Overview: Enterprise Log Pipeline
Imagine you are a backend engineer tasked with building a Production-Ready Server Log Processor. 
Every night, multiple microservices drop raw, semi-structured error logs into an incoming directory.
Your pipeline must safely ingest, parse, aggregate, and archive these files while maintaining strict audit trails and handling corrupted data gracefully."""
from datetime import datetime
import logging
from pathlib import Path
import re
import shutil

# 1. Basic Logging Setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# 2. Setup Directories using pathlib
BASE_DIR = Path("./simple_logs")
INCOMING = BASE_DIR / "incoming"
ARCHIVE = BASE_DIR / "archive"

INCOMING.mkdir(parents=True, exist_ok=True)
ARCHIVE.mkdir(parents=True, exist_ok=True)

# 3. Simple Log Pattern (e.g., 2026-03-30 10:00:00 [AUTH] ERROR: Failed login)
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+ \S+)\s+\[(?P<service>[\w-]+)\]\s+(?P<level>\w+):\s+(?P<message>.+)$"
)


def run_pipeline():
  logging.info("Starting simple log pipeline...")

  # Find all log files
  log_files = list(INCOMING.glob("*.log"))
  if not log_files:
    logging.info("No log files found in incoming directory.")
    return

  for file_path in log_files:
    logging.info(f"Processing: {file_path.name}")

    error_count = 0
    total_lines = 0

    try:
      # Read the log file line by line
      with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
          total_lines += 1
          cleaned = line.strip()

          if not cleaned:
            continue

          match = LOG_PATTERN.match(cleaned)
          if match:
            data = match.groupdict()
            if data["level"] == "ERROR":
              error_count += 1
          else:
            logging.warning(f"Skipping malformed line: {cleaned}")

      logging.info(
          f"Done. Total lines: {total_lines}, Errors found: {error_count}"
      )

      # Move processed file to archive
      destination = ARCHIVE / file_path.name
      shutil.move(str(file_path), str(destination))
      logging.info(f"Archived to: {destination}\n")

    except Exception as e:
      logging.error(f"Failed to process {file_path.name}: {e}")


if __name__ == "__main__":
  run_pipeline()