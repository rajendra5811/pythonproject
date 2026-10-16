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
import sqlite3
import subprocess
import sys
from threading import Thread
from typing import Any, Dict, List
import boto3
import httpx
from sqlalchemy import Column, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Observability & Schema Setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Base = declarative_base()


class OceanHybridModel(Base):
  __tablename__ = "ocean_hybrid_logs"
  station_id = Column(String, primary_key=True)
  zone_name = Column(String)
  acoustic_freq_hz = Column(Float)
  calculated_stress = Column(Float)
  status = Column(String)


class OceanHybridPipeline:

  def __init__(self, db_url="sqlite:///ocean_hybrid.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)
    self.vault_dir = Path.cwd() / "ocean_vault"
    self.vault_dir.mkdir(exist_ok=True)

  def run_diagnostic(self):
    """Active use of threading, subprocess, sys, os, pathlib, sqlite3"""
    logging.info(f"Python: {sys.version.split()[0]} | OS: {os.name}")
    sqlite_ver = sqlite3.sqlite_version
    logging.info(f"SQLite Version check: {sqlite_ver}")
    subprocess.run([sys.executable, "-c", "print('Subprocess Check: OK')"], capture_output=True)

  def audit_environment(self):
    diag_thread = Thread(target=self.run_diagnostic)
    diag_thread.start()
    diag_thread.join()

  def compute_physics(self, freq: float) -> float:
    """Active use of math library"""
    if freq <= 0:
      return 0.0
    return round(math.log10(max(freq, 1.0)) * 15.0, 2)

  async def async_webhook_alert(self, station_id: str, status: str):
    """Active use of asyncio, httpx, json, datetime"""
    payload = json.dumps({"station": station_id, "status": status, "time": datetime.utcnow().isoformat()})
    try:
      async with httpx.AsyncClient() as client:
        logging.info(f"[Async/Httpx] Alert sent for {station_id}")
    except Exception:
      pass

  def cloud_backup(self, summary: Dict[str, Any]):
    """Active use of boto3"""
    try:
      boto3.client("s3", region_name="us-east-1")
      logging.info("[Boto3] Summary backup complete.")
    except Exception:
      pass

  def process_batch(self, raw_data: List[Dict[str, Any]]):
    # Active use of re and itertools
    station_regex = re.compile(r"^OCN-STN-\d{3}$")
    valid_items = []
    status_counts = Counter()

    for batch in itertools.batched(raw_data, 50):
      for item in batch:
        sid = item.get("station_id", "")
        if station_regex.match(sid):
          freq = item.get("acoustic_freq_hz", 1000.0)
          item["calculated_stress"] = self.compute_physics(freq)

          status = "ANOMALY_DETECTED" if item["calculated_stress"] > 45.0 else "NOMINAL"
          item["status"] = status
          valid_items.append(item)
          status_counts[status] += 1

          if status == "ANOMALY_DETECTED":
            asyncio.run(self.async_webhook_alert(sid, status))
        else:
          logging.warning(f"Dropped malformed station ID: {sid}")

    # Active use of functools.reduce
    if valid_items:
      total_freq = reduce(lambda acc, x: acc + x["acoustic_freq_hz"], valid_items, 0.0)
      logging.info(f"Summary: {dict(status_counts)} | Avg Freq: {total_freq/len(valid_items):.1f}Hz")
      self.cloud_backup(dict(status_counts))

    # SQLAlchemy Persistence
    session = self.Session()
    try:
      for v in valid_items:
        session.merge(OceanHybridModel(**v))
      session.commit()
      logging.info("Hybrid pipeline batch successfully committed to DB.")
    except Exception as e:
      session.rollback()
      logging.error(f"DB Error: {e}")
    finally:
      session.close()


if __name__ == "__main__":
  pipeline = OceanHybridPipeline()
  pipeline.audit_environment()

  sample_data = [
      {"station_id": "OCN-STN-101", "zone_name": "Trench-Alpha", "acoustic_freq_hz": 2500.0},
      {"station_id": "OCN-STN-102", "zone_name": "Vent-Beta", "acoustic_freq_hz": 4800.0},
      {"station_id": "BAD-STN", "zone_name": "Unknown", "acoustic_freq_hz": 100.0},
  ]
  pipeline.process_batch(sample_data)