import asyncio
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
from threading import Thread
from typing import Any, Dict, List
import boto3
import httpx
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Setup & Schema
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Base = declarative_base()


class GreenhouseModel(Base):
  __tablename__ = "greenhouse_sensors"
  sensor_id = Column(String, primary_key=True)
  zone = Column(String)
  temperature_c = Column(Float)
  vpd_index = Column(Float)  # Vapor Pressure Deficit
  status = Column(String)


class GreenhousePipeline:

  def __init__(self, db_url="sqlite:///greenhouse_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def audit_system(self):
    """Simple system validation using sys, os, pathlib, subprocess"""
    Path.cwd().joinpath("greenhouse_logs").mkdir(exist_ok=True)
    logging.info(f"Node Active | Python: {sys.version.split()[0]} | OS: {os.name}")
    subprocess.run([sys.executable, "-c", "print('Diagnostics: OK')"], capture_output=True)

  def compute_vpd(self, temp_c: float) -> float:
    """Simple math calculation for vapor pressure index"""
    if temp_c <= 0:
      return 0.0
    return round(math.log10(max(temp_c, 1.0)) * 4.5, 2)

  def process_batch(self, raw_data: List[Dict[str, Any]]):
    # 1. Validation (re) & Grouping (collections.Counter)
    sensor_regex = re.compile(r"^GH-ZONE-\d{3}$")
    valid_items = []
    status_counts = Counter()

    for item in raw_data:
      if sensor_regex.match(item.get("sensor_id", "")):
        temp = item.get("temperature_c", 20.0)
        item["vpd_index"] = self.compute_vpd(temp)

        status = "HEAT_WARNING" if temp > 32.0 else "OPTIMAL"
        item["status"] = status
        valid_items.append(item)
        status_counts[status] += 1
      else:
        logging.warning(f"Dropped invalid sensor ID: {item.get('sensor_id')}")

    # 2. Aggregation (functools.reduce)
    if valid_items:
      total_temp = reduce(lambda acc, x: acc + x["temperature_c"], valid_items, 0.0)
      logging.info(f"Status Summary: {dict(status_counts)} | Avg Temp: {total_temp/len(valid_items):.1f}C")

    # 3. Persistence (SQLAlchemy)
    session = self.Session()
    try:
      for v in valid_items:
        session.merge(GreenhouseModel(**v))
      session.commit()
      logging.info("Greenhouse batch successfully persisted to database.")
    except Exception as e:
      session.rollback()
      logging.error(f"DB Error: {e}")
    finally:
      session.close()


if __name__ == "__main__":
  pipeline = GreenhousePipeline()
  pipeline.audit_system()

  sample_input = [
      {"sensor_id": "GH-ZONE-101", "zone": "Tomato-Bay", "temperature_c": 28.5},
      {"sensor_id": "GH-ZONE-102", "zone": "Lettuce-Bay", "temperature_c": 34.2},
      {"sensor_id": "BAD-ID", "zone": "Unknown", "temperature_c": 22.0},
  ]
  pipeline.process_batch(sample_input)