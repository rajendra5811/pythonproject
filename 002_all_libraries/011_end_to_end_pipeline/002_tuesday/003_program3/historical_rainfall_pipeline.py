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

# 1. Setup Logging & Database
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Base = declarative_base()


class RainfallModel(Base):
  __tablename__ = "historical_rainfall"
  station_id = Column(String, primary_key=True)
  region = Column(String)
  precipitation_mm = Column(Float)
  drought_index = Column(Float)
  status = Column(String)


class RainfallPipeline:

  def __init__(self, db_url="sqlite:///rainfall_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def audit_env(self):
    """Pathlib & Sys validation block"""
    Path.cwd().joinpath("rainfall_data").mkdir(exist_ok=True)
    logging.info(f"Environment OK | Python: {sys.version.split()[0]}")

  def compute_drought_index(self, precipitation: float) -> float:
    """Math library transformation block"""
    if precipitation <= 0:
      return 10.0  # Severe drought indicator
    return round(math.log10(max(precipitation, 1.0)) * 5.2, 2)

  def process_batch(self, raw_data: List[Dict[str, Any]]):
    # 1. Validation block (Regex)
    station_regex = re.compile(r"^RAIN-\d{4}$")
    valid_records = []
    status_counts = Counter()

    for item in raw_data:
      if station_regex.match(item.get("station_id", "")):
        precip = item.get("precipitation_mm", 0.0)
        item["drought_index"] = self.compute_drought_index(precip)

        status = "FLOOD_RISK" if precip > 150.0 else "NORMAL"
        item["status"] = status

        valid_records.append(item)
        status_counts[status] += 1
      else:
        logging.warning(f"Dropped invalid station: {item.get('station_id')}")

    # 2. Aggregation block (Functools & Collections)
    if valid_records:
      total = reduce(lambda acc, x: acc + x["precipitation_mm"], valid_records, 0.0)
      logging.info(f"Status Summary: {dict(status_counts)} | Total Rain: {total}mm")

    # 3. Persistence block (SQLAlchemy)
    session = self.Session()
    try:
      for r in valid_records:
        session.merge(RainfallModel(**r))
      session.commit()
      logging.info("Batch successfully saved to database.")
    except Exception as e:
      session.rollback()
      logging.error(f"DB Error: {e}")
    finally:
      session.close()


if __name__ == "__main__":
  pipeline = RainfallPipeline()
  pipeline.audit_env()

  sample_input = [
      {"station_id": "RAIN-4012", "region": "North-Valley", "precipitation_mm": 175.5},
      {"station_id": "RAIN-8831", "region": "South-Plains", "precipitation_mm": 24.0},
      {"station_id": "BAD-ID", "region": "Unknown", "precipitation_mm": 50.0},
  ]
  pipeline.process_batch(sample_input)