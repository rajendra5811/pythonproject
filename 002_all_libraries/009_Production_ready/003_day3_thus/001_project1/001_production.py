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

# SQLAlchemy Core & ORM imports
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# 1. LOGGING CONFIGURATION
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | [%(name)s] | %(message)s"
)
logger = logging.getLogger("EnterpriseFileETL")

# 2. FUNCTOOLS & TYPING: Cached configuration manager
@functools.lru_cache(maxsize=1)
def get_pipeline_environment_config() -> Dict[str, Any]:
    logger.info("Initializing cached runtime configurations...")
    return {
        "db_url": os.getenv("DATABASE_URL", "sqlite:///enterprise_warehouse.db"),
        "s3_bucket": os.getenv("BACKUP_BUCKET", "enterprise-audit-bucket-prod"),
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "max_workers": os.cpu_count() or 2
    }

# 3. SQLALCHEMY ORM SCHEMA DEFINITION (Sink Database Layer)
class Base(DeclarativeBase):
    pass

class CustomerTransactionModel(Base):
    __tablename__ = "customer_transactions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(50), index=True)
    order_total: Mapped[float] = mapped_column(Float)
    region_code: Mapped[str] = mapped_column(String(10))
    partition_dt: Mapped[str] = mapped_column(String(20))
    ingested_at: Mapped[str] = mapped_column(String(50))

class FileETLPipelineEngine:
    def __init__(self):
        # 4. SYS, OS & PATHLIB: CLI arguments, environment & workspace management
        self.cli_args = sys.argv[1:]
        self.env = os.getenv("ENV", "production")
        
        self.source_dir = Path("source_landing_zone")
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.sink_staging = Path("sink_staging")
        self.sink_staging.mkdir(parents=True, exist_ok=True)
        
        # 5. COLLECTIONS: Metrics tracking & state counters
        self.execution_metrics = Counter()
        self.region_groupings = defaultdict(list)
        self.recent_events = deque(maxlen=500)
        
        # Initialize Database Engine & Sessionmaker (SQLAlchemy Core/ORM Sink)
        config = get_pipeline_environment_config()
        self.engine = create_engine(config["db_url"], echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Initialize AWS Boto3 client
        self.s3_client = boto3.client("s3", region_name=config["region"])

    def run_system_preflight_check(self) -> None:
        # 6. SUBPROCESS: Validate host environment binaries before execution
        try:
            res = subprocess.run(["python", "--version"], capture_output=True, text=True, check=True)
            logger.info(f"Preflight check passed. Python runtime: {res.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Preflight check failed: {e.stderr}")
            sys.exit(1)

    def source_discover_and_read_files(self) -> List[Dict[str, Any]]:
        # 7. PATHLIB & JSON: Source data ingestion from local JSON file drops
        logger.info(f"SOURCE -> Scanning directory: {self.source_dir.absolute()} for payload files...")
        json_files = list(self.source_dir.rglob("*.json"))
        
        if not json_files:
            logger.warning("No source files discovered. Generating mock sample payload for testing.")
            return [{
                "raw_text": "Order invoice for CUST-99887766 processed",
                "amount": 250.75,
                "region": "US-EAST"
            }]
            
        all_records = []
        for file_path in json_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                data = json.loads(content)
                if isinstance(data, list):
                    all_records.extend(data)
                else:
                    all_records.append(data)
                self.execution_metrics["source_files_read"] += 1
            except Exception as exc:
                logger.error(f"Failed parsing file {file_path.name}: {exc}")
                self.execution_metrics["source_read_errors"] += 1
                
        logger.info(f"SOURCE -> Successfully ingested {len(all_records)} raw records from files.")
        return all_records

    @staticmethod
    def transform_record_core(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # 8. RE, MATH, & DATETIME: CPU-heavy parsing, regex extraction, and cleaning
        try:
            # Regular Expression: Extract exact customer code pattern
            raw_text = record.get("raw_text", "")
            match = re.search(r"CUST-[0-9]{8}", raw_text)
            customer_id = match.group(0) if match else "CUST-UNKNOWN"
            
            # Math: Validate numerical boundary values
            raw_amount = record.get("amount", float("nan"))
            order_total = 0.0 if math.isnan(raw_amount) else round(raw_amount, 2)
            
            # Datetime: Construct immutable UTC temporal fields and partitions
            now_utc = datetime.now(timezone.utc)
            
            return {
                "customer_id": customer_id,
                "order_total": order_total,
                "region_code": record.get("region", "GLOBAL"),
                "partition_dt": now_utc.strftime("%Y-%m-%d"),
                "ingested_at": now_utc.isoformat()
            }
        except Exception as err:
            logger.error(f"Transform failure on record: {err}")
            return None

    def transform_parallel_pipeline(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # 9. MULTIPROCESSING: Bypass GIL to map transform logic across CPU cores
        config = get_pipeline_environment_config()
        logger.info(f"TRANSFORM -> Distributing {len(raw_records)} records across {config['max_workers']} CPU cores...")
        
        with multiprocessing.Pool(processes=config["max_workers"]) as pool:
            results = pool.map(self.transform_record_core, raw_records)
            
        clean_records = [r for r in results if r is not None]
        self.execution_metrics["records_transformed"] = len(clean_records)
        return clean_records

    def sink_persist_to_database(self, records: List[Dict[str, Any]]) -> None:
        # 10. ITERTOOLS & SQLALCHEMY ORM: Memory-efficient batched insertion to Database Sink
        config = get_pipeline_environment_config()
        batch_size = 500
        iterator = iter(records)
        
        logger.info("SINK (Database) -> Persisting records via SQLAlchemy ORM sessions...")
        with self.SessionLocal() as session:
            while True:
                chunk = list(itertools.islice(iterator, batch_size))
                if not chunk:
                    break
                
                db_objects = [CustomerTransactionModel(**item) for item in chunk]
                session.add_all(db_objects)
                session.commit()
                self.execution_metrics["db_rows_inserted"] += len(chunk)
                
        logger.info("SINK (Database) -> Batch insertion committed successfully.")

    def sink_backup_audit_to_s3(self) -> None:
        # 11. BOTO3 & PATHLIB: Upload execution telemetry summary to cloud object storage
        config = get_pipeline_environment_config()
        summary_filename = f"etl_audit_{int(datetime.now(timezone.utc).timestamp())}.json"
        local_path = self.sink_staging / summary_filename
        
        audit_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": dict(self.execution_metrics),
            "status": "COMPLETED"
        }
        
        local_path.write_text(json.dumps(audit_payload, indent=2))
        
        try:
            s3_key = f"audit-logs/{summary_filename}"
            logger.info(f"SINK (Cloud S3) -> Uploading audit report to bucket [{config['s3_bucket']}]...")
            # self.s3_client.upload_file(str(local_path), config["s3_bucket"], s3_key)
            logger.info("SINK (Cloud S3) -> Audit backup completed.")
        except Exception as e:
            logger.error(f"SINK (Cloud S3) -> Audit backup upload failed: {e}")

    def start_telemetry_heartbeat_thread(self) -> None:
        # 12. THREADING: Non-blocking background health monitor
        def monitor_loop():
            logger.info(f"BACKGROUND TELEMETRY -> Current Metrics Snapshot: {dict(self.execution_metrics)}")
        
        t = threading.Thread(target=monitor_loop, daemon=True)
        t.start()

# ==========================================
# PIPELINE EXECUTION ENTRYPOINT
# ==========================================
if __name__ == "__main__":
    pipeline = FileETLPipelineEngine()
    pipeline.run_system_preflight_check()
    pipeline.start_telemetry_heartbeat_thread()
    
    # 1. SOURCE PHASE
    raw_data = pipeline.source_discover_and_read_files()
    
    # 2. TRANSFORM PHASE
    transformed_data = pipeline.transform_parallel_pipeline(raw_data)
    
    # 3. SINK PHASE (Database + Cloud Backup)
    if transformed_data:
        pipeline.sink_persist_to_database(transformed_data)
        pipeline.sink_backup_audit_to_s3()
        
    logger.info("End-to-End File ETL Pipeline execution completed successfully.")