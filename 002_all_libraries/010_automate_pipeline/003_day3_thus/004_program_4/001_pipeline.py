from datetime import datetime
from functools import reduce
import itertools
import json
import logging
from pathlib import Path
from typing import Any, Dict, List
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    MetaData,
    String,
    Table,
    create_engine,
)

# 1. Observability Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("IncrementalOrderPipeline")

# 2. Database Setup using SQLAlchemy Core
engine = create_engine("sqlite:///warehouse.db")
metadata = MetaData()

orders_table = Table(
    "fact_orders",
    metadata,
    Column("order_id", String, primary_key=True),
    Column("customer_id", String),
    Column("total_amount", Float),
    Column("status", String),
    Column("created_at", DateTime),
)

# Create tables if they don't exist
metadata.create_all(engine)


class IncrementalPipeline:

  def __init__(self, state_file: str):
    self.state_path = Path(state_file)

  def _get_last_sync_time(self) -> datetime:
    """Reads state file to ensure incremental processing (no duplicate pulls)."""
    if self.state_path.exists():
      with open(self.state_path, "r") as f:
        data = json.load(f)
        return datetime.fromisoformat(data.get("last_sync"))
    # Default fallback baseline if no state exists
    return datetime(2026, 1, 1, 0, 0, 0)

  def _save_state(self, sync_time: datetime):
    """Persists the watermark state for future runs."""
    with open(self.state_path, "w") as f:
      json.dump({"last_sync": sync_time.isoformat()}, f)

  def extract_source_data(self) -> List[Dict[str, Any]]:
    """Simulates extracting raw incremental orders from an upstream source system."""
    last_sync = self._get_last_sync_time()
    logger.info(f"Extracting records modified since watermark: {last_sync}")

    # Mock raw database or API payload
    raw_incoming_data = [
        {
            "order_id": "ORD-501",
            "customer_id": "C-10",
            "amount": 100.0,
            "status": "COMPLETED",
            "created_at": "2026-03-31T10:30:00",
        },
        {
            "order_id": "ORD-502",
            "customer_id": "C-12",
            "amount": 250.0,
            "status": "PENDING",
            "created_at": "2026-03-31T11:15:00",
        },
        {
            "order_id": "ORD-503",
            "customer_id": "C-05",
            "amount": 50.0,
            "status": "CANCELLED",
            "created_at": "2026-03-31T12:00:00",
        },
    ]

    # Filter strictly for records newer than last sync watermark
    new_records = [
        r
        for r in raw_incoming_data
        if datetime.fromisoformat(r["created_at"]) > last_sync
    ]
    return new_records

  def transform_data(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transforms records: filters out cancelled orders and applies tax enrichment."""
    logger.info("Transforming records: filtering and computing taxes...")

    # 1. Filter out cancelled orders using functional filtering
    active_orders = filter(lambda x: x["status"] != "CANCELLED", records)

    # 2. Enrich rows (add a 5% tax calculation) using map
    transformed = []
    for order in active_orders:
      order_copy = order.copy()
      order_copy["total_amount"] = round(order_copy["amount"] * 1.05, 2)
      order_copy["created_at"] = datetime.fromisoformat(
          order_copy["created_at"]
      )
      transformed.append(order_copy)

    return transformed

  def load_data(self, records: List[Dict[str, Any]]):
    """Loads transformed records into the database using SQLAlchemy Core."""
    if not records:
      logger.info("No new records to load.")
      return

    logger.info(f"Loading {len(records)} records into SQLAlchemy Core target...")
    with engine.begin() as connection:
      # Using Core insert statement
      statement = orders_table.insert()
      connection.execute(statement, records)

    # Update state watermark to the newest timestamp processed
    max_timestamp = max(r["created_at"] for r in records)
    self._save_state(max_timestamp)
    logger.info(f"Pipeline batch complete. State updated to {max_timestamp}")

  def run(self):
    raw_data = self.extract_source_data()
    clean_data = self.transform_data(raw_data)
    self.load_data(clean_data)


if __name__ == "__main__":
  pipeline = IncrementalPipeline(state_file="pipeline_state.json")
  pipeline.run()