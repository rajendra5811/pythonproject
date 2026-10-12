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
logger = logging.getLogger("SpaceLaunchTelemetryPipeline")

# 2. Database Persistence Setup (SQLAlchemy ORM)
Base = declarative_base()


class LaunchTelemetryModel(Base):
  __tablename__ = "space_launch_telemetry"
  launch_id = Column(String, primary_key=True)
  vehicle_name = Column(String)
  altitude_km = Column(Float)
  reentry_velocity_kmps = Column(Float)
  heat_flux_mw = Column(Float)
  launch_status = Column(String)
  recorded_at = Column(String)


class SpaceLaunchTelemetryPipeline:

  def __init__(self, db_url="sqlite:///space_launch_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def audit_mission_environment(self):
    """System validation using sys, os, and pathlib"""
    logger.info(
        f"Launch Control Node Active | Python: {sys.version.split()[0]} | OS:"
        f" {os.name}"
    )
    launch_vault = Path.cwd() / "launch_telemetry_vault"
    launch_vault.mkdir(exist_ok=True)
    logger.info(
        f"Mission telemetry secure vault verified via pathlib: {launch_vault}"
    )

  def calculate_heat_flux(self, velocity_kmps: float, altitude_km: float) -> float:
    """Uses math library to compute thermal shield heat flux during re-entry"""
    if altitude_km <= 0 or velocity_kmps <= 0:
      return 0.0
    # Aerodynamic thermal equation approximation
    flux = 1.74 * math.sqrt(velocity_kmps) * math.exp(-altitude_km / 85.0)
    return round(flux, 2)

  def process_launch_batch(self, raw_telemetry: List[Dict[str, Any]]):
    # Regex pattern for Launch Identification Codes (e.g., LAUNCH-SRV-9012)
    launch_id_regex = re.compile(r"^LAUNCH-SRV-\d{4}$")
    valid_launches = []
    status_counts = Counter()

    for record in raw_telemetry:
      launch_id = record.get("launch_id", "")
      if launch_id_regex.match(launch_id):
        velocity = record.get("reentry_velocity_kmps", 7.8)
        altitude = record.get("altitude_km", 120.0)

        # Compute physics metrics via math module
        heat_flux = self.calculate_heat_flux(velocity, altitude)
        record["heat_flux_mw"] = heat_flux

        # Orbital Re-Entry Safety Rule
        status = (
            "THERMAL_SHIELD_CRITICAL"
            if heat_flux > 12.0 or altitude < 50.0
            else "NOMINAL_ORBITAL"
        )
        record["launch_status"] = status

        valid_launches.append(record)
        status_counts[status] += 1
      else:
        logger.warning(
            f"Mission Control Alert: Dropped malformed Launch ID '{launch_id}'"
        )

    # Aggregate total re-entry velocity across batch using functools.reduce
    if valid_launches:
      total_vel = reduce(
          lambda acc, x: acc + x["reentry_velocity_kmps"], valid_launches, 0.0
      )
      avg_vel = round(total_vel / len(valid_launches), 2)
      logger.info(
          f"Mission Status Summary (collections): {dict(status_counts)}"
      )
      logger.info(f"Average Re-Entry Velocity Recorded: {avg_vel} km/s")

    # SQLAlchemy ORM Session Commit to Mission Control Database
    session = self.Session()
    try:
      for v in valid_launches:
        db_record = LaunchTelemetryModel(
            launch_id=v["launch_id"],
            vehicle_name=v["vehicle_name"],
            altitude_km=v["altitude_km"],
            reentry_velocity_kmps=v["reentry_velocity_kmps"],
            heat_flux_mw=v["heat_flux_mw"],
            launch_status=v["launch_status"],
            recorded_at=datetime.utcnow().isoformat(),
        )
        session.merge(db_record)
      session.commit()
      logger.info(
          "Successfully transmitted and persisted validated launch telemetry"
          " batch to Mission database."
      )
    except Exception as e:
      session.rollback()
      logger.error(f"Mission Control database transaction failure: {e}")
      raise
    finally:
      session.close()


# --- Execution Example ---
if __name__ == "__main__":
  pipeline = SpaceLaunchTelemetryPipeline()
  pipeline.audit_mission_environment()

  sample_launch_payload = [
      {
          "launch_id": "LAUNCH-SRV-4019",
          "vehicle_name": "Titan-Ascent I",
          "altitude_km": 110.5,
          "reentry_velocity_kmps": 7.4,
      },
      {
          "launch_id": "LAUNCH-SRV-4020",
          "vehicle_name": "Ares-Orbiter II",
          "altitude_km": 42.0,
          "reentry_velocity_kmps": 9.1,
      },
      {
          "launch_id": "INVALID-LAUNCH-ID",
          "vehicle_name": "Ghost Booster",
          "altitude_km": 100.0,
          "reentry_velocity_kmps": 7.0,
      },
  ]

  pipeline.process_launch_batch(sample_launch_payload)