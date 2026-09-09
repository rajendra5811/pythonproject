import os
import boto3
from sqlalchemy import create_engine, Table, MetaData, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import Dict, Any, List

class CloudPersistenceLoader:
    def __init__(self, db_connection_url: str, bucket_name: str):
        # 1. boto3: Initialize S3 cloud client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket_name = bucket_name
        
        # 2. SQLAlchemy Core: Initialize engine and metadata schema registry
        self.engine = create_engine(db_connection_url)
        self.metadata = MetaData()
        
        # Define target analytical table schema programmatically
        self.target_table = Table(
            "fact_telemetry_events",
            self.metadata,
            autoload_with=self.engine # Introspects existing table schema from database
        )

    def fetch_object_from_s3(self, object_key: str) -> bytes:
        """Fetch raw file or dataset payload directly from an S3 cloud data lake using boto3."""
        print(f"Fetching s3://{self.bucket_name}/{object_key}...")
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_key)
        return response['Body'].read()

    def bulk_upsert_to_database(self, records: List[Dict[str, Any]]) -> None:
        """Perform high-performance bulk upserts using SQLAlchemy Core expressions."""
        if not records:
            print("No records to persist.")
            return

        print(f"Persisting {len(records)} records to database via SQLAlchemy Core...")
        
        with self.engine.begin() as connection:
            # Build idempotent UPSERT statement (PostgreSQL dialect example)
            stmt = pg_insert(self.target_table).values(records)
            
            # On primary key conflict, update the payload and timestamp columns
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['event_id'], # Unique constraint column
                set_={
                    "payload": stmt.excluded.payload,
                    "updated_at": stmt.excluded.updated_at
                }
            )
            
            connection.execute(upsert_stmt)
        print("Persistence transaction committed successfully.")

# Example execution simulation
if __name__ == "__main__":
    db_url = "postgresql://user:pass@localhost:5432/warehouse_db"
    loader = CloudPersistenceLoader(db_url, "my-data-lake-bucket")
    
    # simulated payload batch
    sample_records = [
        {"event_id": "evt_101", "payload": '{"status": "ok"}', "updated_at": "2026-06-01T12:00:00Z"}
    ]
    # loader.bulk_upsert_to_database(sample_records)