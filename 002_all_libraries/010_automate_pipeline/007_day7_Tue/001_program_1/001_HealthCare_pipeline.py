from collections import Counter
from datetime import datetime
from functools import reduce
import json
import logging
import math
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Observability Setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# 2. Database Setup (SQLAlchemy ORM)
Base = declarative_base()


class PatientVitalsModel(Base):
  __tablename__ = "patient_vitals"
  mrn = Column(String, primary_key=True)
  patient_name = Column(String)
  heart_rate = Column(Integer)
  blood_pressure = Column(String)
  bmi = Column(Float)
  triage_status = Column(String)
  recorded_at = Column(String)


class HealthcarePipeline:

  def __init__(self, db_url="sqlite:///healthcare_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def audit_environment(self):
    """Uses os, sys, and pathlib for secure clinical workspace verification"""
    logging.info(
        f"Healthcare Pipeline Node | Python: {sys.version.split()[0]} | OS:"
        f" {os.name}"
    )
    clinical_path = Path.cwd() / "clinical_records"
    clinical_path.mkdir(exist_ok=True)
    logging.info(f"Clinical workspace verified via pathlib: {clinical_path}")

  def calculate_bmi(self, weight_kg: float, height_m: float) -> float:
    """Uses math library to accurately calculate Body Mass Index"""
    if height_m <= 0:
      return 0.0
    return round(weight_kg / math.pow(height_m, 2), 1)

  def process_vitals_batch(self, raw_records: List[Dict[str, Any]]):
    # Regex for standard Medical Record Number validation (e.g., MRN-459201)
    mrn_regex = re.compile(r"^MRN-\d{6}$")
    valid_records = []
    triage_counts = Counter()

    for record in raw_records:
      if mrn_regex.match(record.get("mrn", "")):
        hr = record.get("heart_rate", 75)
        # Automatic clinical triage assessment
        triage = "CRITICAL" if hr > 120 or hr < 50 else "STABLE"
        record["triage_status"] = triage

        # Compute BMI
        record["bmi"] = self.calculate_bmi(
            record.get("weight_kg", 70.0), record.get("height_m", 1.75)
        )

        valid_records.append(record)
        triage_counts[triage] += 1
      else:
        logging.warning(
            f"Invalid MRN format dropped: {record.get('mrn', 'UNKNOWN')}"
        )

    # Compute aggregate batch metrics using functools.reduce
    if valid_records:
      total_hr = reduce(lambda acc, x: acc + x["heart_rate"], valid_records, 0)
      avg_hr = round(total_hr / len(valid_records), 1)
      logging.info(f"Batch Triage Breakdown (collections): {dict(triage_counts)}")
      logging.info(f"Average Patient Heart Rate: {avg_hr} BPM")

    # SQLAlchemy ORM Persistence
    session = self.Session()
    try:
      for v in valid_records:
        db_record = PatientVitalsModel(
            mrn=v["mrn"],
            patient_name=v["patient_name"],
            heart_rate=v["heart_rate"],
            blood_pressure=v["blood_pressure"],
            bmi=v["bmi"],
            triage_status=v["triage_status"],
            recorded_at=datetime.utcnow().isoformat(),
        )
        session.merge(db_record)
      session.commit()
      logging.info(
          "Successfully synced valid patient vitals batch to database via"
          " SQLAlchemy."
      )
    except Exception as e:
      session.rollback()
      logging.error(f"Database sync failed: {e}")
    finally:
      session.close()


# --- Execution Example ---
if __name__ == "__main__":
  pipeline = HealthcarePipeline()
  pipeline.audit_environment()

  sample_incoming_vitals = [
      {
          "mrn": "MRN-459201",
          "patient_name": "Jane Doe",
          "heart_rate": 130,
          "blood_pressure": "140/90",
          "weight_kg": 68.5,
          "height_m": 1.65,
      },
      {
          "mrn": "MRN-883921",
          "patient_name": "John Smith",
          "heart_rate": 72,
          "blood_pressure": "120/80",
          "weight_kg": 82.0,
          "height_m": 1.80,
      },
      {
          "mrn": "INVALID-MRN",
          "patient_name": "Bad Record",
          "heart_rate": 80,
          "blood_pressure": "110/70",
          "weight_kg": 70.0,
          "height_m": 1.70,
      },
  ]

  pipeline.process_vitals_batch(sample_incoming_vitals)