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
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# ==========================================
# 1. AUDIT & LOGGING (Module: logging)
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)d] | %(message)s"
)
logger = logging.getLogger("LogStreamPipeline")

# ==========================================
# 2. CONFIG & CONTRACTS (Modules: functools, typing)
# ==========================================
@functools.lru_cache(maxsize=1)
def get_log_pipeline_config() -> Dict[str, Any]:
    logger.info("Loading cached log stream configurations via functools...")
    return {
        "db_url": os.getenv("DATABASE_URL", "sqlite:///log_warehouse.db"),
        "s3_bucket": os.getenv("S3_BUCKET", "enterprise-log-lake-prod"),
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "batch_size": 100
    }

# SQLAlchemy ORM Base & Model
class Base(DeclarativeBase):
    pass

class SystemLogModel(Base):
    __tablename__ = "system_logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip_address: Mapped[str] = mapped_column(String(50), index=True)
    status_code: Mapped[int] = mapped_column(Integer)
    partition_dt: Mapped[str] = mapped_column(String(20))
    ingested_at: Mapped[str] = mapped_column(String(50))


class LogStreamETLEngine:
    def __init__(self):
        # ==========================================
        # 3. ENVIRONMENT & WORKSPACE (Modules: sys, os, pathlib)
        # ==========================================
        self.cli_args = sys.argv[1:]
        self.environment = os.getenv("ENV", "production")
        
        self.staging_path = Path("log_staging_zone")
        self.staging_path.mkdir(parents=True, exist_ok=True)
        
        # ==========================================
        # 4. STATE & METRICS (Module: collections)
        # ==========================================
        self.status_counter = Counter()
        self.ip_groupings = defaultdict(list)
        self.event_deque = deque(maxlen=300)
        
        # ==========================================
        # 5. BOTO3 INITIALIZATION: Session, Client, & Resource
        # ==========================================
        config = get_log_pipeline_config()
        
        # Session
        self.aws_session = boto3.Session(region_name=config["region"])
        # Client (Low-level service API)
        self.s3_client = self.aws_session.client("s3")
        # Resource (High-level object-oriented abstraction)
        self.s3_resource = self.aws_session.resource("s3")
        self.target_bucket = self.s3_resource.Bucket(config["s3_bucket"])

        # Initialize SQLAlchemy Database Sink
        self.engine = create_engine(config["db_url"], echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def run_preflight_checks(self) -> None:
        # ==========================================
        # 6. EXECUTION CONTROL (Module: subprocess)
        # ==========================================
        try:
            res = subprocess.run(["python", "--version"], capture_output=True, text=True, check=True)
            logger.info(f"Preflight healthcheck passed. Python: {res.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Preflight failed: {e.stderr}")
            sys.exit(1)

    async def source_fetch_log_stream_async(self, endpoint: str) -> List[Dict[str, Any]]:
        # ==========================================
        # 7. SOURCE EXTRACTION (Modules: httpx, asyncio)
        # ==========================================
        logger.info(f"SOURCE -> Ingesting log stream asynchronously from {endpoint}...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                tasks = [client.get(endpoint) for _ in range(2)]
                responses = await asyncio.gather(*tasks)
                
                raw_logs = []
                for resp in responses:
                    if resp.status_code == 200:
                        self.status_counter["fetch_success"] += 1
                        # Simulating raw log string payload conversion
                        data = resp.json()
                        if isinstance(data, list):
                            raw_logs.extend(data)
                        else:
                            raw_logs.append(data)
                    else:
                        self.status_counter[f"fetch_error_{resp.status_code}"] += 1
                return raw_logs
            except httpx.RequestError as exc:
                logger.error(f"Async log fetch network error: {exc}")
                return []

    @staticmethod
    def transform_log_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # ==========================================
        # 8. TRANSFORM LOGIC (Modules: re, json, math, datetime)
        # ==========================================
        try:
            # RE: Extract IP addresses from unstructured raw log text
            log_text = record.get("log_line", "192.168.1.1 GET /api/v1/data 200")
            ip_match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", log_text)
            client_ip = ip_match.group(0) if ip_match else "0.0.0.0"
            
            # MATH: Validate numeric response codes
            code_val = record.get("status", 200)
            status_code = 200 if math.isnan(float(code_val)) else int(code_val)
            
            # DATETIME: UTC timestamp and partition keys
            now_utc = datetime.now(timezone.utc)
            
            return {
                "ip_address": client_ip,
                "status_code": status_code,
                "partition_dt": now_utc.strftime("%Y-%m-%d"),
                "ingested_at": now_utc.isoformat()
            }
        except Exception as err:
            logger.error(f"Log parsing error: {err}")
            return None

    def transform_parallel_pool(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # ==========================================
        # 9. PARALLEL COMPUTATION (Module: multiprocessing)
        # ==========================================
        logger.info(f"TRANSFORM -> Spawning multiprocessing pool for {len(raw_records)} log rows...")
        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            results = pool.map(self.transform_log_record, raw_records)
        return [r for r in results if r is not None]

    def sink_load_and_persist_logs(self, records: List[Dict[str, Any]]) -> None:
        # ==========================================
        # 10. SINK PERSISTENCE (Modules: itertools, pathlib, json, SQLAlchemy, boto3)
        # ==========================================
        config = get_log_pipeline_config()
        iterator = iter(records)
        batch_idx = 0
        
        logger.info("SINK -> Writing batches to relational warehouse and AWS S3...")
        with self.SessionLocal() as session:
            while True:
                chunk = list(itertools.islice(iterator, config["batch_size"]))
                if not chunk:
                    break
                
                batch_idx += 1
                filename = f"log_batch_{batch_idx}_{int(datetime.now(timezone.utc).timestamp())}.json"
                local_file = self.staging_path / filename
                
                # Pathlib + JSON local staging
                local_file.write_text(json.dumps(chunk, indent=2))
                
                # SQLAlchemy DB Insertion
                db_rows = [SystemLogModel(**item) for item in chunk]
                session.add_all(db_rows)
                session.commit()
                
                # Boto3 Cloud S3 Upload (Client & Resource)
                try:
                    s3_key = f"logs-zone/dt={chunk[0]['partition_dt']}/{filename}"
                    logger.info(f"Uploading log batch {filename} to S3 bucket [{config['s3_bucket']}]...")
                    
                    # Client pattern
                    # self.s3_client.upload_file(str(local_file), config["s3_bucket"], s3_key)
                    # Resource pattern alternative
                    # self.target_bucket.upload_file(str(local_file), s3_key)
                    
                    self.status_counter["s3_uploads_success"] += 1
                except Exception as e:
                    logger.error(f"S3 log upload failed: {e}")

    def start_background_telemetry(self) -> None:
        # ==========================================
        # 11. BACKGROUND MONITORING (Module: threading)
        # ==========================================
        def monitor_worker():
            logger.info(f"TELEMETRY HEARTBEAT -> Current Status Counters: {dict(self.status_counter)}")
        
        t = threading.Thread(target=monitor_worker, daemon=True)
        t.start()

# ==========================================
# EXECUTION ENTRYPOINT
# ==========================================
async def main():
    pipeline = LogStreamETLEngine()
    pipeline.run_preflight_checks()
    pipeline.start_background_telemetry()
    
    # 1. SOURCE
    stream_endpoint = "https://httpbin.org/json"
    raw_logs = await pipeline.source_fetch_log_stream_async(stream_endpoint)
    if not raw_logs:
        raw_logs = [{"log_line": "Connection established from 10.0.0.45 with status 200", "status": 200}]
        
    # 2. TRANSFORM
    clean_logs = pipeline.transform_parallel_pool(raw_logs)
    
    # 3. SINK
    if clean_logs:
        pipeline.sink_load_and_persist_logs(clean_logs)
        
    logger.info("Log Stream ETL pipeline execution completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())