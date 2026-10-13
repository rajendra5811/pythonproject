from collections import Counter
from datetime import datetime
from functools import reduce
import itertools
import json
import logging
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List
import asyncio
import httpx
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Enterprise Observability Setup (logging)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("VolcanoSeismicPipeline")

# 2. Database Persistence Setup (SQLAlchemy ORM)
Base = declarative_base()


class SeismicSensorModel(Base):
  __tablename__ = "volcano_seismic_readings"
  station_id = Column(String, primary_key=True)
  volcano_name = Column(String)
  harmonic_amplitude_mm = Column(Float)
  moment_magnitude = Column(Float)
  alert_level = Column(String)
  recorded_at = Column(String)


class VolcanoSeismicPipeline:

  def __init__(self, db_url="sqlite:///volcano_seismic_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def audit_system_environment(self):
    """System validation using sys, os, pathlib, and subprocess"""
    logger.info(
        f"Seismic Node Active | Python: {sys.version.split()[0]} | OS:"
        f" {os.name}"
    )
    seismic_dir = Path.cwd() / "seismic_vault"
    seismic_dir.mkdir(exist_ok=True)
    logger.info(f"Seismic vault verified via pathlib: {seismic_dir}")

    # Subprocess check for local system integrity
    echo_command = (
        [os.environ.get("COMSPEC", "cmd.exe"), "/c", "echo", "Subprocess Diagnostics: OK"]
        if os.name == "nt"
        else ["echo", "Subprocess Diagnostics: OK"]
    )
    result = subprocess.run(echo_command, capture_output=True, text=True, check=True)
    logger.info(result.stdout.strip())

  def calculate_moment_magnitude(self, amplitude_mm: float) -> float:
    """Uses math library to compute seismic moment magnitude from tremor amplitude"""
    if amplitude_mm <= 0:
      return 0.0
    # Richter/Moment Magnitude logarithmic scale approximation
    magnitude = (2.0 / 3.0) * math.log10(amplitude_mm * 1000.0) + 1.0
    return round(magnitude, 2)

  def process_seismic_batch(self, raw_readings: List[Dict[str, Any]]):
    # Regex pattern for Station IDs (e.g., SEIS-VOLC-9012)
    station_regex = re.compile(r"^SEIS-VOLC-\d{4}$")
    valid_readings = []
    alert_counts = Counter()

    for record in raw_readings:
      station_id = record.get("station_id", "")
      if station_regex.match(station_id):
        amplitude = record.get("harmonic_amplitude_mm", 1.5)

        # Compute physics metrics via math module
        mag = self.calculate_moment_magnitude(amplitude)
        record["moment_magnitude"] = mag

        # Volcanic Eruption Alert Rule
        alert = "RED_ERUPTION_WARNING" if mag > 5.5 or amplitude > 25.0 else "GREEN_NORMAL"
        record["alert_level"] = alert

        valid_readings.append(record)
        alert_counts[alert] += 1
      else:
        logger.warning(
            f"Seismic Network Alert: Dropped malformed Station ID '{station_id}'"
        )

    # Aggregate total amplitude across batch using functools.reduce
    if valid_readings:
      total_amp = reduce(
          lambda acc, x: acc + x["harmonic_amplitude_mm"], valid_readings, 0.0
      )
      avg_amp = round(total_amp / len(valid_readings), 2)
      logger.info(
          f"Seismic Alert Summary (collections): {dict(alert_counts)}"
      )
      logger.info(f"Average Harmonic Tremor Amplitude: {avg_amp} mm")

    # SQLAlchemy ORM Session Commit to Volcanology Database
    session = self.Session()
    try:
      for v in valid_readings:
        db_record = SeismicSensorModel(
            station_id=v["station_id"],
            volcano_name=v["volcano_name"],
            harmonic_amplitude_mm=v["harmonic_amplitude_mm"],
            moment_magnitude=v["moment_magnitude"],
            alert_level=v["alert_level"],
            recorded_at=datetime.utcnow().isoformat(),
        )
        session.merge(db_record)
      session.commit()
      logger.info(
          "Successfully persisted validated seismic telemetry batch to"
          " Volcanology database via SQLAlchemy."
      )
    except Exception as e:
      session.rollback()
      logger.error(f"Database transaction failure: {e}")
      raise
    finally:
      session.close()


# --- Execution Example ---
if __name__ == "__main__":
  pipeline = VolcanoSeismicPipeline()
  pipeline.audit_system_environment()

  sample_seismic_payload = [
      {
          "station_id": "SEIS-VOLC-4019",
          "volcano_name": "Mt. Etna Sector Alpha",
          "harmonic_amplitude_mm": 3.2,
      },
      {
          "station_id": "SEIS-VOLC-4020",
          "volcano_name": "Ring of Fire Caldera",
          "harmonic_amplitude_mm": 32.5,
      },
      {
          "station_id": "INVALID-STATION",
          "volcano_name": "Ghost Sensor",
          "harmonic_amplitude_mm": 1.0,
      },
  ]

  pipeline.process_seismic_batch(sample_seismic_payload)