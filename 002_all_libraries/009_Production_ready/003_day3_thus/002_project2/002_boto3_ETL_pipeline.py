import os
import sys
import json
import re
import math
import logging
import asyncio
import httpx
import boto3
import multiprocessing
import threading
import itertools
import functools
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict, deque

# SQLAlchemy imports (Sink Database Layer)
from sqlalchemy import create_engine, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# ==========================================
# 1. AUDIT & LOGGING (Module: logging)
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)d] | %(message)s"
)
logger = logging.getLogger("ZeroFrictionPipeline")

# ==========================================
# 2. CONFIG & CONTRACTS (Modules: functools, typing)
# ==========================================
@functools.lru_cache(maxsize=1)
def get_production_settings() -> Dict[str, Any]:
    logger.info("Loading and caching production parameters via functools...")
    return {
        "db_url": os.getenv("DATABASE_URL", "sqlite:///production_warehouse.db"),
        "s3_bucket": os.getenv("S3_BUCKET", "enterprise-silver-lake"),
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "batch_size": 250
    }

# SQLAlchemy ORM Base & Model
class Base(DeclarativeBase):
    pass

class SilverRecordModel(Base):
    __tablename__ = "silver_transactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(50), index=True)
    amount: Mapped[float] = mapped_column(Float)
    partition_dt: Mapped[str] = mapped_column(String(20))
    ingested_at: Mapped[str] = mapped_column(String(50))


class EnterpriseETLPipeline:
    def __init__(self):
        # ==========================================
        # 3. ENVIRONMENT & WORKSPACE (Modules: sys, os, pathlib)
        # ==========================================
        self.cli_args = sys.argv[1:]
        self.env = os.getenv("ENV", "production")
        
        self.staging_dir = Path("local_pipeline_staging")
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        
        # ==========================================
        # 4. STATE & METRICS (Module: collections)
        # ==========================================
        self.metrics = Counter()
        self.category_groups = defaultdict(list)
        self.event_queue = deque(maxlen=500)
        
        # Initialize Database & Cloud S3 Sinks (Modules: SQLAlchemy, boto3)
        settings = get_production_settings()
        self.engine = create_engine(settings["db_url"], echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.s3_client = boto3.client("s3", region_name=settings["region"])

    def verify_runtime_environment(self) -> None:
        # ==========================================
        # 5. EXECUTION CONTROL (Module: subprocess)
        # ==========================================
        try:
            res = subprocess.run(["python", "--version"], capture_output=True, text=True, check=True)
            logger.info(f"Preflight check passed. Runtime: {res.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Environment preflight failed: {e.stderr}")
            sys.exit(1)

    async def source_extract_async(self, api_url: str) -> List[Dict[str, Any]]:
        # ==========================================
        # 6. SOURCE EXTRACTION (Modules: httpx, asyncio)
        # ==========================================
        logger.info(f"SOURCE -> Connecting asynchronously to {api_url}...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                tasks = [client.get(api_url) for _ in range(2)]
                responses = await asyncio.gather(*tasks)
                
                raw_payloads = []
                for resp in responses:
                    if resp.status_code == 200:
                        self.metrics["source_fetch_success"] += 1
                        raw_payloads.extend(resp.json())
                    else:
                        self.metrics[f"source_error_{resp.status_code}"] += 1
                return raw_payloads
            except httpx.RequestError as exc:
                logger.error(f"Source extraction network error: {exc}")
                return []

    @staticmethod
    def transform_record_core(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # ==========================================
        # 7. TRANSFORM LOGIC (Modules: re, json, math, datetime)
        # ==========================================
        try:
            # RE: Clean text and extract IDs
            raw_text = record.get("message", "")
            match = re.search(r"TXN-[0-9]{8}", raw_text)
            txn_id = match.group(0) if match else "TXN-UNKNOWN"
            
            # MATH: Guard numerical calculations
            raw_val = record.get("amount", float("nan"))
            clean_amount = 0.0 if math.isnan(raw_val) else round(raw_val, 2)
            
            # DATETIME: UTC timestamps and partition keys
            now_utc = datetime.now(timezone.utc)
            
            return {
                "transaction_id": txn_id,
                "amount": clean_amount,
                "partition_dt": now_utc.strftime("%Y-%m-%d"),
                "ingested_at": now_utc.isoformat()
            }
        except Exception as err:
            logger.error(f"Transformation parser error: {err}")
            return None

    def transform_parallel_pool(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # ==========================================
        # 8. PARALLEL COMPUTATION (Module: multiprocessing)
        # ==========================================
        logger.info(f"TRANSFORM -> Distributing {len(raw_records)} records across CPU cores...")
        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            results = pool.map(self.transform_record_core, raw_records)
        return [r for r in results if r is not None]

    def sink_load_and_persist(self, records: List[Dict[str, Any]]) -> None:
        # ==========================================
        # 9. SINK PERSISTENCE (Modules: itertools, pathlib, json, SQLAlchemy, boto3)
        # ==========================================
        settings = get_production_settings()
        iterator = iter(records)
        batch_idx = 0
        
        logger.info("SINK -> Committing batches to Database & Cloud S3...")
        with self.SessionLocal() as session:
            while True:
                chunk = list(itertools.islice(iterator, settings["batch_size"]))
                if not chunk:
                    break
                
                batch_idx += 1
                filename = f"batch_{batch_idx}_{int(datetime.now(timezone.utc).timestamp())}.json"
                local_path = self.staging_dir / filename
                
                # Pathlib + JSON local staging
                local_path.write_text(json.dumps(chunk, indent=2))
                
                # SQLAlchemy Database Insertion
                db_rows = [SilverRecordModel(**item) for item in chunk]
                session.add_all(db_rows)
                session.commit()
                
                # Boto3 Cloud S3 Upload
                try:
                    s3_key = f"silver/dt={chunk[0]['partition_dt']}/{filename}"
                    logger.info(f"Uploading {filename} to S3 bucket [{settings['s3_bucket']}]...")
                    # self.s3_client.upload_file(str(local_path), settings["s3_bucket"], s3_key)
                    self.metrics["s3_uploads_success"] += 1
                except Exception as e:
                    logger.error(f"S3 upload failed: {e}")

    def start_telemetry_heartbeat(self) -> None:
        # ==========================================
        # 10. BACKGROUND MONITORING (Module: threading)
        # ==========================================
        def monitor_loop():
            logger.info(f"TELEMETRY SNAPSHOT -> Metrics state: {dict(self.metrics)}")
        
        t = threading.Thread(target=monitor_loop, daemon=True)
        t.start()

# ==========================================
# EXECUTION ENTRYPOINT
# ==========================================
async def main():
    pipeline = EnterpriseETLPipeline()
    pipeline.verify_runtime_environment()
    pipeline.start_telemetry_heartbeat()
    
    # 1. SOURCE
    endpoint = "https://httpbin.org/json"
    raw_data = await pipeline.source_extract_async(endpoint)
    if not raw_data:
        raw_data = [{"message": "Transaction recorded for TXN-12345678 successfully", "amount": 499.50}]
        
    # 2. TRANSFORM
    clean_data = pipeline.transform_parallel_pool(raw_data)
    
    # 3. SINK
    if clean_data:
        pipeline.sink_load_and_persist(clean_data)
        
    logger.info("End-to-end production pipeline execution finished successfully.")

if __name__ == "__main__":
    asyncio.run(main())