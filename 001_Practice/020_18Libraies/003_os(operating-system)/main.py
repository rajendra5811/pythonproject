# Read DB URLs, environment variables, file paths
import os
from sqlalchemy import create_engine

engine = create_engine(
    os.getenv("DATABASE_URL")
)
#CLI arguments, debugging, runtime configuration
import sys

print(sys.argv)
#Timestamps, audit columns, filtering records by date
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
#Aggregating query results, Counter, defaultdict
from collections import Counter

grades = ["A", "A", "B", "A", "C"]

print(Counter(grades))