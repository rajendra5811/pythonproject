from datetime import datetime
import json
import logging
from pathlib import Path
import shutil
import sqlite3

# 1. Directory & Path Setup
BASE_DIR = Path(__file__).resolve().parent
INCOMING_DIR = BASE_DIR / "data" / "incoming"
PROCESSED_DIR = BASE_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "output"
DB_FILE = BASE_DIR / "ev_stations.db"
LOG_FILE = OUTPUT_DIR / "pipeline.log"


def setup_environment():
  for folder in [INCOMING_DIR, PROCESSED_DIR, OUTPUT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
  logging.basicConfig(
      filename=LOG_FILE,
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s",
  )


# 2. Database Initialization
def create_database():
  conn = sqlite3.connect(DB_FILE)
  conn.execute(
      """
        CREATE TABLE IF NOT EXISTS charging_logs (
            session_id TEXT PRIMARY KEY,
            station_code TEXT NOT NULL,
            kwh_delivered REAL NOT NULL,
            duration_minutes INTEGER NOT NULL,
            loaded_at TEXT NOT NULL
        )
    """
  )
  conn.commit()
  return conn


# 3. Core Processing Function
def process_file(conn, file_path):
  logging.info(f"Processing file: {file_path.name}")
  try:
    with file_path.open("r", encoding="utf-8") as f:
      record = json.load(f)

    # Basic validation check
    if not record.get("session_id") or not record.get("station_code"):
      logging.warning(f"Rejected {file_path.name}: Missing required fields.")
      shutil.move(file_path, PROCESSED_DIR / f"rejected_{file_path.name}")
      return False

    loaded_at = datetime.now().isoformat()

    # Insert into Database
    conn.execute(
        """
            INSERT OR REPLACE INTO charging_logs 
            (session_id, station_code, kwh_delivered, duration_minutes, loaded_at)
            VALUES (?, ?, ?, ?, ?)
        """,
        (
            record["session_id"],
            record["station_code"],
            record["kwh_delivered"],
            record["duration_minutes"],
            loaded_at,
        ),
    )

    # Move file to processed folder on success
    shutil.move(file_path, PROCESSED_DIR / file_path.name)
    logging.info(f"Successfully processed and moved {file_path.name}")
    return True

  except Exception as e:
    logging.error(f"Error processing {file_path.name}: {e}")
    return False


# 4. Main Pipeline Runner
def run_pipeline():
  setup_environment()
  conn = None

  try:
    files = list(INCOMING_DIR.glob("*.json"))
    if not files:
      print("No incoming files found to process.")
      return

    conn = create_database()
    conn.execute("BEGIN")

    success_count = 0
    for file_path in files:
      if process_file(conn, file_path):
        success_count += 1

    conn.commit()
    print(
        f"Pipeline complete. Successfully processed {success_count} of"
        f" {len(files)} files."
    )

  except Exception as e:
    if conn:
      conn.rollback()
    logging.exception(f"Pipeline crashed: {e}")
    print(f"Pipeline failed: {e}")

  finally:
    if conn:
      conn.close()


if __name__ == "__main__":
  run_pipeline()