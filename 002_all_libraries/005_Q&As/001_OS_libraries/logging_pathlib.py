import logging
from pathlib import Path
import httpx


logging.basicConfig(level=logging.INFO)

path = Path("data/students.json")

if path.exists():
    logging.info("Input file found")

logging.info("Processing started")


logging.basicConfig(level=logging.INFO)

response = httpx.get(
    "https://api.example.com/students"
)

if response.is_success:
    logging.info("API request successful")
else:
    logging.error(
        "API request failed: %s",
        response.status_code
    )