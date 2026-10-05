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

# 1. Logging Setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# 2. SQLAlchemy Database Setup
Base = declarative_base()


class InventoryModel(Base):
  __tablename__ = "warehouse_inventory"
  sku = Column(String, primary_key=True)
  name = Column(String)
  quantity = Column(Integer)
  price = Column(Float)
  status = Column(String)


class InventoryPipeline:

  def __init__(self, db_url="sqlite:///inventory_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def audit_environment(self):
    """Uses os, sys, and pathlib for environment setup"""
    logging.info(
        f"Inventory System Node | Python: {sys.version.split()[0]} | OS:"
        f" {os.name}"
    )
    warehouse_path = Path.cwd() / "warehouse_data"
    warehouse_path.mkdir(exist_ok=True)
    logging.info(f"Warehouse workspace verified via pathlib: {warehouse_path}")

  def process_stock_batch(self, raw_items: List[Dict[str, Any]]):
    # Regex for standard SKU validation (e.g., SKU-ELC-1001)
    sku_regex = re.compile(r"^SKU-[A-Z]{3}-\d{4}$")
    valid_items = []
    status_counts = Counter()

    for item in raw_items:
      if sku_regex.match(item.get("sku", "")):
        qty = item.get("quantity", 0)
        # Classify inventory levels
        status = "IN_STOCK" if qty > 10 else "LOW_STOCK"
        item["status"] = status
        valid_items.append(item)
        status_counts[status] += 1
      else:
        logging.warning(
            f"Invalid SKU format dropped: {item.get('sku', 'UNKNOWN')}"
        )

    # Compute total inventory valuation using functools and math
    total_valuation = reduce(
        lambda acc, x: acc + (x["quantity"] * x["price"]), valid_items, 0.0
    )
    logging.info(f"Inventory Breakdown (collections): {dict(status_counts)}")
    logging.info(f"Total Warehouse Asset Valuation: ${total_valuation:,.2f}")

    # SQLAlchemy ORM Persist
    session = self.Session()
    try:
      for v in valid_items:
        record = InventoryModel(
            sku=v["sku"],
            name=v["name"],
            quantity=v["quantity"],
            price=v["price"],
            status=v["status"],
        )
        session.merge(record)
      session.commit()
      logging.info(
          "Successfully synced valid inventory batch to SQLite database via"
          " SQLAlchemy."
      )
    except Exception as e:
      session.rollback()
      logging.error(f"Database sync failed: {e}")
    finally:
      session.close()


# --- Execution Example ---
if __name__ == "__main__":
  pipeline = InventoryPipeline()
  pipeline.audit_environment()

  sample_incoming_inventory = [
      {
          "sku": "SKU-ELC-1001",
          "name": "Wireless Mouse",
          "quantity": 45,
          "price": 25.99,
      },
      {
          "sku": "SKU-OFF-2042",
          "name": "Standing Desk",
          "quantity": 4,
          "price": 299.99,
      },
      {
          "sku": "INVALID-SKU",
          "name": "Damaged Box",
          "quantity": 100,
          "price": 5.00,
      },
  ]

  pipeline.process_stock_batch(sample_incoming_inventory)