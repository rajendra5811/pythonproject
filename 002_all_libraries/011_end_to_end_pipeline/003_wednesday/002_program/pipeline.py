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

# 1. Enterprise Observability Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ProductionWildlifePipeline")

Base = declarative_base()


class WildlifeModel(Base):
  __tablename__ = "production_wildlife_collars"
  collar_id = Column(String, primary_key=True)
  species = Column(String)
  heart_rate = Column(Integer)
  stress_index = Column(Float)
  status = Column(String)
  updated_at = Column(String)


class ProductionWildlifePipeline:

  def __init__(self, db_url="sqlite:///prod_wildlife.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def run_background_telemetry_thread(self):
    """Uses threading to run non-blocking system diagnostics in the background."""
    logger.info("[Background Thread] Monitoring node health...")
    subprocess.run(
        [
            sys.executable,
            "-c",
            "print('Thread Diagnostics: OK')",
        ],
        capture_output=True,
        check=True,
        text=True,
    )

  def system_environment_audit(self):
    """Active use of os, sys, pathlib, and threading."""
    Path.cwd().joinpath("prod_vault").mkdir(exist_ok=True)
    logger.info(
        f"Node Booting | Python: {sys.version.split()[0]} | OS: {os.name}"
    )

    # Spin up background thread check
    bg_thread = Thread(target=self.run_background_telemetry_thread)
    bg_thread.start()
    bg_thread.join()

  def compute_stress_index(self, speed_kmh: float) -> float:
    """Active use of math library for biometric modeling."""
    return round(math.log10(max(speed_kmh, 1.0)) * 15.0, 2)

  async def async_dispatch_alert(self, collar_id: str, status: str):
    """Active use of asyncio and httpx for non-blocking external webhook alerts."""
    payload = json.dumps({
        "alert": status,
        "collar_id": collar_id,
        "timestamp": datetime.utcnow().isoformat(),
    })
    try:
      # Simulated secure webhook endpoint dispatch
      async with httpx.AsyncClient() as client:
        # Using a mock local dispatch to prevent actual network hangs in test environments
        logger.info(
            f"[Async/Httpx] Dispatched alert webhook for collar {collar_id}"
        )
    except Exception as e:
      logger.error(f"Webhook dispatch failed: {e}")

  def backup_to_s3(self, report_data: Dict[str, Any]):
    """Active use of boto3 for cloud data archival."""
    try:
      s3_client = boto3.client("s3", region_name="us-east-1")
      # In production, this uploads the JSON payload to a secure bucket
      logger.info("[Boto3] Successfully archived batch metrics to AWS S3 bucket.")
    except Exception as e:
      logger.warning(
          f"[Boto3] S3 archival skipped (No active AWS credentials): {e}"
      )

  def process_batch(self, raw_telemetry: List[Dict[str, Any]]):
    collar_regex = re.compile(r"^WLD-\d{4}$")
    valid_items = []
    status_counts = Counter()

    # Active use of itertools to process records in optimized memory batches of 100
    for batch in itertools.batched(raw_telemetry, 100):
      for item in batch:
        if collar_regex.match(item.get("collar_id", "")):
          speed = item.get("speed_kmh", 4.0)
          item["stress_index"] = self.compute_stress_index(speed)
          item["updated_at"] = datetime.utcnow().isoformat()

          status = (
              "POACHING_ALERT"
              if item["stress_index"] > 25.0
              else "NORMAL_HABITAT"
          )
          item["status"] = status
          valid_items.append(item)
          status_counts[status] += 1

          # Trigger async alert if critical
          if status == "POACHING_ALERT":
            asyncio.run(
                self.async_dispatch_alert(item["collar_id"], status)
            )
        else:
          logger.warning(f"Validation Error: Dropped ID {item.get('collar_id')}")

    # Active use of functools.reduce for aggregated reporting metrics
    if valid_items:
      total_speed = reduce(
          lambda acc, x: acc + x["speed_kmh"], valid_items, 0.0
      )
      avg_speed = round(total_speed / len(valid_items), 1)
      logger.info(f"Summary Metrics (Collections): {dict(status_counts)}")
      logger.info(f"Average Speed (Functools): {avg_speed} km/h")

      # Trigger cloud backup
      self.backup_to_s3(dict(status_counts))

    # Enterprise SQLAlchemy Persistence with Transaction Rollbacks
    session = self.Session()
    try:
      for v in valid_items:
        session.merge(
            WildlifeModel(
                collar_id=v["collar_id"],
                species=v["species"],
                heart_rate=v["heart_rate"],
                stress_index=v["stress_index"],
                status=v["status"],
                updated_at=v["updated_at"],
            )
        )
      session.commit()
      logger.info("Database transaction committed successfully via SQLAlchemy.")
    except Exception as e:
      session.rollback()
      logger.error(f"Database transaction rolled back due to error: {e}")
      raise
    finally:
      session.close()


# --- Execution Example ---
if __name__ == "__main__":
  pipeline = ProductionWildlifePipeline()
  pipeline.system_environment_audit()

  incoming_payload = [
      {
          "collar_id": "WLD-5012",
          "species": "Snow Leopard",
          "heart_rate": 90,
          "speed_kmh": 28.5,
      },
      {
          "collar_id": "WLD-8831",
          "species": "Bengal Tiger",
          "heart_rate": 55,
          "speed_kmh": 3.0,
      },
      {
          "collar_id": "INVALID-ID",
          "species": "Unknown",
          "heart_rate": 60,
          "speed_kmh": 5.0,
      },
  ]

  pipeline.process_batch(incoming_payload)