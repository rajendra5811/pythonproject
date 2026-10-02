from collections import Counter
import asyncio
from datetime import datetime
from functools import reduce
import itertools
import json
import logging
import math
import multiprocessing
import os
from pathlib import Path
import re
import subprocess
import sys
from threading import Thread
from typing import Any, Dict, List
import httpx
from sqlalchemy import Column, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Observability Setup (logging)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# 2. Database Setup (SQLAlchemy Core & ORM)
Base = declarative_base()


class BankTransactionModel(Base):
  __tablename__ = "banking_ledger"
  tx_id = Column(String, primary_key=True)
  account = Column(String)
  amount = Column(Float)
  processed_at = Column(String)


class CompactBankingPipeline:

  def __init__(self, db_url="sqlite:///banking_core.db"):
    self.engine = create_engine(db_url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def system_audit_check(self):
    """Uses os, sys, pathlib, and subprocess for system health checks"""
    logging.info(
        f"Running on Python version: {sys.version.split()[0]} | OS:"
        f" {os.name}"
    )
    current_path = Path.cwd()
    logging.info(f"Workspace Path verified via pathlib: {current_path}")

    # Subprocess command check
    echo_command = (
        ["cmd", "/c", "echo", "Security Audit: OK"]
        if os.name == "nt"
        else ["echo", "Security Audit: OK"]
    )
    result = subprocess.run(echo_command, capture_output=True, text=True, check=True)
    logging.info(result.stdout.strip())

  def calculate_risk_score(self, amount: float) -> float:
    """Uses math library for risk compounding calculation"""
    return round(amount * math.log10(max(amount, 10)), 2)

  def process_batch(self, raw_transactions: List[Dict[str, Any]]):
    # Uses itertools and functools for functional data aggregation
    totals = reduce(lambda acc, x: acc + x["amount"], raw_transactions, 0.0)
    logging.info(f"Total incoming batch volume computed via functools: ${totals}")

    # Regex validation & Collections grouping
    valid_txs = []
    statuses = Counter()
    tx_regex = re.compile(r"^TX-\d+$")

    for tx in raw_transactions:
      if tx_regex.match(tx["tx_id"]):
        valid_txs.append(tx)
        statuses[tx.get("status", "PENDING")] += 1

    logging.info(f"Status breakdown (collections.Counter): {dict(statuses)}")

    # SQLAlchemy ORM Session Commit
    session = self.Session()
    try:
      for t in valid_txs:
        record = BankTransactionModel(
            tx_id=t["tx_id"],
            account=t["account"],
            amount=t["amount"],
            processed_at=datetime.utcnow().isoformat(),
        )
        session.merge(record)
      session.commit()
      logging.info("Successfully committed valid banking batch to SQLAlchemy ORM.")
    except Exception as e:
      session.rollback()
      logging.error(f"Database error: {e}")
    finally:
      session.close()


# --- Execution Example ---
if __name__ == "__main__":
  pipeline = CompactBankingPipeline()
  pipeline.system_audit_check()

  sample_incoming_data = [
      {"tx_id": "TX-1001", "account": "ACC-5501", "amount": 2500.00, "status": "APPROVED"},
      {"tx_id": "TX-1002", "account": "ACC-8842", "amount": 150.50, "status": "PENDING"},
      {"tx_id": "INVALID-ID", "account": "ACC-1100", "amount": 99.99, "status": "FAILED"},
  ]
  
  pipeline.process_batch(sample_incoming_data)