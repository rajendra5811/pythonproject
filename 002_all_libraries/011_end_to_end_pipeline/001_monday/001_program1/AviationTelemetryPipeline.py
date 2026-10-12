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
logger = logging.getLogger("AviationTelemetryPipeline")

# 2. Database Persistence Setup (SQLAlchemy ORM)
Base = declarative_base()


class FlightTelemetryModel(Base):
  __tablename__ = "flight_telemetry"
  flight_id = Column(String, primary_key=True)
  airline = Column(String)
  altitude_ft = Column(Integer)
  ground_speed_knots = Column(Float)
  fuel_efficiency_score = Column(Float)
  flight_status = Column(String)
  recorded_at = Column(String)


class AviationTelemetryPipeline:

  def __init__(self, db_url="sqlite:///aviation_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def system_environment_check(self):
    """Phase 1-3 Validation using sys, os, and pathlib"""
    logger.info(
        f"Aviation Node Active | Python: {sys.version.split()[0]} | OS:"
        f" {os.name}"
    )
    airspace_dir = Path.cwd() / "airspace_incoming"
    airspace_dir.mkdir(exist_ok=True)
    logger.info(f"Airspace ingest directory verified via pathlib: {airspace_dir}")

  def calculate_fuel_efficiency(
      self, speed_knots: float, altitude_ft: int
  ) -> float:
    """Uses math library for aerodynamic efficiency calculations"""
    # Complex mathematical model for air density vs fuel burn index
    if altitude_ft <= 0:
      return 0.0
    efficiency = (speed_knots * math.log(altitude_ft)) / (math.pi * 10.0)
    return round(efficiency, 2)

  def process_flight_batch(self, raw_telemetry: List[Dict[str, Any]]):
    # Regex pattern for Flight IDs (e.g., DL-4921, UA-8831)
    flight_regex = re.compile(r"^[A-Z]{2}-\d{4}$")
    valid_flights = []
    status_counts = Counter()

    for record in raw_telemetry:
      flight_id = record.get("flight_id", "")
      if flight_regex.match(flight_id):
        speed = record.get("ground_speed_knots", 450.0)
        altitude = record.get("altitude_ft", 30000)

        # Apply math transformation
        eff_score = self.calculate_fuel_efficiency(speed, altitude)
        record["fuel_efficiency_score"] = eff_score

        # Airspace Safety Rule: Vector violation if high speed below 10,000 ft
        status = (
            "VECTOR_VIOLATION" if altitude < 10000 and speed > 350 else "NOMINAL"
        )
        record["flight_status"] = status

        valid_flights.append(record)
        status_counts[status] += 1
      else:
        logger.warning(
            f"Airspace Security Alert: Dropped malformed Flight ID '{flight_id}'"
        )

    # Aggregate fleet metrics using functools.reduce
    if valid_flights:
      total_speed = reduce(
          lambda acc, x: acc + x["ground_speed_knots"], valid_flights, 0.0
      )
      avg_speed = round(total_speed / len(valid_flights), 1)
      logger.info(
          f"Airspace Status Summary (collections): {dict(status_counts)}"
      )
      logger.info(f"Average Fleet Ground Speed: {avg_speed} Knots")

    # SQLAlchemy ORM Session Commit
    session = self.Session()
    try:
      for v in valid_flights:
        db_record = FlightTelemetryModel(
            flight_id=v["flight_id"],
            airline=v["airline"],
            altitude_ft=v["altitude_ft"],
            ground_speed_knots=v["ground_speed_knots"],
            fuel_efficiency_score=v["fuel_efficiency_score"],
            flight_status=v["flight_status"],
            recorded_at=datetime.utcnow().isoformat(),
        )
        session.merge(db_record)
      session.commit()
      logger.info(
          "Successfully persisted validated flight telemetry batch via"
          " SQLAlchemy."
      )
    except Exception as e:
      session.rollback()
      logger.error(f"Database transaction failure: {e}")
      raise
    finally:
      session.close()


# --- Execution Example ---
if __name__ == "__main__":
  pipeline = AviationTelemetryPipeline()
  pipeline.system_environment_check()

  sample_flight_data = [
      {
          "flight_id": "DL-4921",
          "airline": "Delta",
          "altitude_ft": 35000,
          "ground_speed_knots": 480.5,
      },
      {
          "flight_id": "UA-8831",
          "airline": "United",
          "altitude_ft": 8500,
          "ground_speed_knots": 380.0,
      },
      {
          "flight_id": "INVALID-ID",
          "airline": "Unknown",
          "altitude_ft": 20000,
          "ground_speed_knots": 400.0,
      },
  ]

  pipeline.process_flight_batch(sample_flight_data)