from pathlib import Path
from collections import Counter
from datetime import datetime
import json
import logging
import re

BASE_DIR = Path("data")
SOURCE_FILE = BASE_DIR / "orders.json"
OUTPUT_FILE = BASE_DIR / "clean_orders.json"
LOG_FILE = BASE_DIR / "pipeline.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

def extract_orders(source_file: Path) -> list[dict]:
    """Read orders from JSON."""

    logger.info("Reading source file: %s", source_file)

    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    with source_file.open("r", encoding="utf-8") as file:
        orders = json.load(file)

    if not isinstance(orders, list):
        raise ValueError("Expected JSON file to contain a list of orders")

    logger.info("Extracted %d orders", len(orders))

    return orders

def validate_order(order: dict) -> bool:
    """Validate required order fields."""

    required_fields = {
        "order_id",
        "customer",
        "email",
        "city",
        "amount",
        "order_date"
    }

    if not required_fields.issubset(order):
        return False

    if not isinstance(order["amount"], (int, float)):
        return False

    if order["amount"] <= 0:
        return False

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", order["email"]):
        return False

    return True

def transform_order(order: dict) -> dict:
    """Clean and enrich one order."""

    transformed = order.copy()

    transformed["customer"] = transformed["customer"].strip().title()
    transformed["city"] = transformed["city"].strip().upper()
    transformed["email"] = transformed["email"].strip().lower()

    transformed["amount"] = round(float(transformed["amount"]), 2)

    order_date = datetime.strptime(
        transformed["order_date"],
        "%Y-%m-%d"
    )

    transformed["order_date"] = order_date.strftime("%Y-%m-%d")

    transformed["processed_at"] = datetime.now().isoformat()

    return transformed

def transform_orders(orders: list[dict]) -> list[dict]:
    """Validate and transform orders."""

    clean_orders = []

    for order in orders:

        if not validate_order(order):
            logger.warning(
                "Invalid order skipped: %s",
                order.get("order_id", "UNKNOWN")
            )
            continue

        clean_order = transform_order(order)
        clean_orders.append(clean_order)

    logger.info(
        "Valid orders after transformation: %d",
        len(clean_orders)
    )

    return clean_orders

def calculate_city_counts(orders: list[dict]) -> Counter:
    """Count orders by city."""

    cities = [order["city"] for order in orders]

    return Counter(cities)

def load_orders(
    orders: list[dict],
    output_file: Path
) -> None:
    """Write transformed orders to JSON."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            orders,
            file,
            indent=4
        )

    logger.info(
        "Loaded %d orders into %s",
        len(orders),
        output_file
    )

def run_pipeline() -> None:

    logger.info("========== PIPELINE START ==========")

    try:

        orders = extract_orders(SOURCE_FILE)
        
        clean_orders = transform_orders(orders)

        city_counts = calculate_city_counts(clean_orders)
   
        load_orders(
            clean_orders,
            OUTPUT_FILE
        )

        logger.info(
            "City distribution: %s",
            dict(city_counts)
        )

        logger.info("========== PIPELINE SUCCESS ==========")

    except Exception as error:

        logger.exception(
            "Pipeline failed: %s",
            error
        )

        raise

if __name__ == "__main__":
    run_pipeline()