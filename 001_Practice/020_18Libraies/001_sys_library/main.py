import logging

logging.basicConfig(level=logging.INFO)

logging.info("Loading students")
logging.error("Database connection failed")

from pathlib import Path

data_dir = Path("data")
files = list(data_dir.glob("*.csv"))

import boto3

s3 = boto3.client("s3")

s3.upload_file(
    "students.csv",
    "my-bucket",
    "raw/students.csv"
)