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

# 1. Enterprise Observability Setup (logging)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("HeadquartersCrashTestingPipeline")

# 2. Database Persistence Setup (SQLAlchemy ORM)
Base = declarative_base()


class CrashTestRecordModel(Base):
  __tablename__ = "hq_crash_test_telemetry"
  test_id = Column(String, primary_key=True)
  aircraft_model = Column(String)
  impact_velocity_mps = Column(Float)
  max_g_force = Column(Float)
  kinetic_energy_kj = Column(Float)
  structural_rating = Column(String)
  transmitted_at = Column(String)


class CrashTestingPipeline:

  def __init__(self, db_url="sqlite:///hq_crash_testing.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def audit_headquarters_environment(self):
    """Phase 1-3 Validation using sys, os, and pathlib"""
    logger.info(
        f"HQ Receiver Active | Python: {sys.version.split()[0]} | OS:"
        f" {os.name}"
    )
    hq_vault_path = Path.cwd() / "hq_crash_telemetry_vault"
    hq_vault_path.mkdir(exist_ok=True)
    logger.info(
        f"Headquarters secure telemetry vault verified via pathlib:"
        f" {hq_vault_path}"
    )

  def calculate_kinetic_energy(self, mass_kg: float, velocity_mps: float) -> float:
    """Uses math library to compute impact kinetic energy (0.5 * m * v^2 in kJ)"""
    if mass_kg <= 0 or velocity_mps <= 0:
      return 0.0
    energy_joules = 0.5 * mass_kg * math.pow(velocity_mps, 2)
    return round(energy_joules / 1000.0, 2)  # Convert to Kilojoules

  def process_hq_telemetry_batch(self, raw_telemetry: List[Dict[str, Any]]):
    # Regex pattern for Crash Test Incident IDs (e.g., TST-CRASH-4019)
    test_id_regex = re.compile(r"^TST-CRASH-\d{4}$")
    valid_reports = []
    rating_counts = Counter()

    for record in raw_telemetry:
      test_id = record.get("test_id", "")
      if test_id_regex.match(test_id):
        mass = record.get("aircraft_mass_kg", 5000.0)
        velocity = record.get("impact_velocity_mps", 75.0)
        g_force = record.get("max_g_force", 12.0)

        # Compute physics metrics via math module
        ke_kj = self.calculate_kinetic_energy(mass, velocity)
        record["kinetic_energy_kj"] = ke_kj

        # Headquarters Structural Safety Rating Rule
        rating = (
            "CATASTROPHIC_FAILURE" if g_force > 25.0 or ke_kj > 15000.0 else "SURVIVABLE"
        )
        record["structural_rating"] = rating

        valid_reports.append(record)
        rating_counts[rating] += 1
      else:
        logger.warning(
            f"HQ Security Alert: Dropped malformed Crash Test ID '{test_id}'"
        )

    # Aggregate total kinetic energy impact across batch using functools.reduce
    if valid_reports:
      total_ke = reduce(
          lambda acc, x: acc + x["kinetic_energy_kj"], valid_reports, 0.0
      )
      avg_ke = round(total_ke / len(valid_reports), 2)
      logger.info(f"Headquarters Structural Rating Summary (collections): {dict(rating_counts)}")
      logger.info(f"Average Impact Kinetic Energy Recorded: {avg_ke} kJ")

    # SQLAlchemy ORM Session Commit to HQ Database
    session = self.Session()
    try:
      for v in valid_reports:
        db_record = CrashTestRecordModel(
            test_id=v["test_id"],
            aircraft_model=v["aircraft_model"],
            impact_velocity_mps=v["impact_velocity_mps"],
            max_g_force=v["max_g_force"],
            kinetic_energy_kj=v["kinetic_energy_kj"],
            structural_rating=v["structural_rating"],
            transmitted_at=datetime.utcnow().isoformat(),
        )
        session.merge(db_record)
      session.commit()
      logger.info("Successfully transmitted and persisted validated crash telemetry batch to Headquarters database.")
    except Exception as e:
      session.rollback()
      logger.error(f"Headquarters database transaction failure: {e}")
      raise
    finally:
      session.close()


# --- Execution Example ---
if __name__ == "__main__":
  pipeline = CrashTestingPipeline()
  pipeline.audit_headquarters_environment()

  sample_crash_test_payload = [
      {
          "test_id": "TST-CRASH-9021",
          "aircraft_model": "X-Jet Alpha",
          "aircraft_mass_kg": 6200.0,
          "impact_velocity_mps": 65.0,
          "max_g_force": 14.5,
      },
      {
          "test_id": "TST-CRASH-9022",
          "aircraft_model": "X-Jet Beta",
          "aircraft_mass_kg": 7500.0,
          "impact_velocity_mps": 95.0,
          "max_g_force": 31.0,
      },
      {
          "test_id": "INVALID-TEST-ID",
          "aircraft_model": "Corrupted Rig",
          "aircraft_mass_kg": 5000.0,
          "impact_velocity_mps": 50.0,
          "max_g_force": 10.0,
      },
  ]

  pipeline.process_hq_telemetry_batch(sample_crash_test_payload)