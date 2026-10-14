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

# 1. Observability & DB Setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Base = declarative_base()


class WildlifeModel(Base):
  __tablename__ = "wildlife_collars"
  collar_id = Column(String, primary_key=True)
  species = Column(String)
  heart_rate = Column(Integer)
  stress_index = Column(Float)
  status = Column(String)


class WildlifePipeline:

  def __init__(self, db_url="sqlite:///wildlife_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def system_audit(self):
    """Integrates os, sys, pathlib, subprocess"""
    Path.cwd().joinpath("wildlife_vault").mkdir(exist_ok=True)
    sys_info = sys.version.split()[0]
    logging.info(f"System Node OK | Python: {sys_info} | OS: {os.name}")
    subprocess.run(
        [
            sys.executable,
            "-c",
            "print('Security Subprocess Check: Passed')",
        ],
        capture_output=True,
        check=True,
        text=True,
    )

  def compute_stress(self, movement_speed: float) -> float:
    """Integrates math library"""
    return round(math.log10(max(movement_speed, 1.0)) * 12.5, 2)

  def process_batch(self, raw_telemetry: List[Dict[str, Any]]):
    # 1. Validation (re) & Grouping (collections.Counter)
    collar_regex = re.compile(r"^WLD-\d{4}$")
    valid_items = []
    status_counts = Counter()

    for item in raw_telemetry:
      if collar_regex.match(item.get("collar_id", "")):
        speed = item.get("speed_kmh", 5.0)
        item["stress_index"] = self.compute_stress(speed)

        status = (
            "POACHING_ALERT"
            if item["stress_index"] > 20.0
            else "NORMAL_HABITAT"
        )
        item["status"] = status
        valid_items.append(item)
        status_counts[status] += 1
      else:
        logging.warning(f"Dropped bad collar ID: {item.get('collar_id')}")

    # 2. Aggregation (functools.reduce)
    if valid_items:
      total_speed = reduce(lambda acc, x: acc + x["speed_kmh"], valid_items, 0.0)
      logging.info(f"Summary: {dict(status_counts)} | Avg Speed: {total_speed/len(valid_items):.1f}km/h")

    # 3. Persistence (SQLAlchemy ORM)
    session = self.Session()
    try:
      for v in valid_items:
        session.merge(WildlifeModel(
            collar_id=v["collar_id"],
            species=v["species"],
            heart_rate=v["heart_rate"],
            stress_index=v["stress_index"],
            status=v["status"]
        ))
      session.commit()
      logging.info("Wildlife batch successfully persisted to database.")
    except Exception as e:
      session.rollback()
      logging.error(f"DB Error: {e}")
    finally:
      session.close()


if __name__ == "__main__":
  pipeline = WildlifePipeline()
  pipeline.system_audit()

  incoming_payload = [
      {"collar_id": "WLD-1002", "species": "Black Rhino", "heart_rate": 85, "speed_kmh": 22.4},
      {"collar_id": "WLD-4091", "species": "African Elephant", "heart_rate": 45, "speed_kmh": 2.1},
      {"collar_id": "BAD-ID", "species": "Unknown", "heart_rate": 60, "speed_kmh": 5.0}
  ]
  pipeline.process_batch(incoming_payload)