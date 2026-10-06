import json
from pathlib import Path
import re
import sqlite3

# 1. Database Setup
DB_PATH = Path("simple_healthcare.db")


def init_database():
  conn = sqlite3.connect(DB_PATH)
  conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            mrn TEXT PRIMARY KEY,
            name TEXT,
            heart_rate INTEGER,
            triage_status TEXT
        )
    """)
  conn.commit()
  conn.close()


def process_healthcare_data():
  init_database()
  input_file = Path("healthcare_input.json")

  if not input_file.exists():
    print(f"Error: Could not find {input_file}")
    return

  # Load JSON dataset
  with open(input_file, "r", encoding="utf-8") as f:
    records = json.load(f)

  # Regex to validate MRN format (e.g., MRN-102938)
  mrn_pattern = re.compile(r"^MRN-\d{6}$")

  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  processed_count = 0

  for record in records:
    mrn = record.get("mrn", "")

    # Validate MRN
    if mrn_pattern.match(mrn):
      hr = record.get("heart_rate", 75)
      triage = "CRITICAL" if hr > 120 or hr < 50 else "STABLE"

      # Insert or update record in database
      cursor.execute(
          "INSERT OR REPLACE INTO patients (mrn, name, heart_rate,"
          " triage_status) VALUES (?, ?, ?, ?)",
          (mrn, record.get("patient_name"), hr, triage),
      )
      processed_count += 1
    else:
      print(f"Skipping malformed record with MRN: {mrn}")

  conn.commit()
  conn.close()
  print(f"\nPipeline complete! Successfully saved {processed_count} records.")


if __name__ == "__main__":
  process_healthcare_data()