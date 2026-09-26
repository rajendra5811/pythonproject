import asyncio
import functools
import itertools
import json
import logging
import math
import multiprocessing
import os
import re
import subprocess
import sys
import threading

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

import boto3
import httpx


# ============================================================
# 1. DATA CONTRACTS
# ============================================================

class Order(TypedDict, total=False):
    order_id: int
    customer_id: int
    customer_name: str
    email: str
    city: str

    quantity: int
    unit_price: float
    subtotal: float
    tax: float
    shipping: float
    total: float

    category: str
    processed_at: str


class Config:
    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        customer_api: str | None,
        s3_bucket: str | None,
        s3_key: str | None,
    ):
        self.input_path = input_path
        self.output_path = output_path
        self.customer_api = customer_api
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key


# ============================================================
# 2. LOGGING
# ============================================================

def configure_logging() -> None:

    Path("logs").mkdir(
        parents=True,
        exist_ok=True
    )

    logging.basicConfig(
        level=logging.INFO,

        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(threadName)s | "
            "%(message)s"
        ),

        handlers=[
            logging.FileHandler(
                "logs/order_pipeline.log",
                encoding="utf-8"
            ),

            logging.StreamHandler()
        ]
    )


logger = logging.getLogger("order_pipeline")


# ============================================================
# 3. SOURCE — LOCAL JSON
# ============================================================

def extract_orders_from_file(
    input_path: Path
) -> list[dict[str, Any]]:

    logger.info(
        "Reading order source: %s",
        input_path
    )

    if not input_path.exists():

        raise FileNotFoundError(
            f"Order source does not exist: {input_path}"
        )

    with input_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):

        raise ValueError(
            "Order source must contain a JSON list"
        )

    logger.info(
        "Extracted %d orders",
        len(data)
    )

    return data


# ============================================================
# 4. SOURCE — CUSTOMER REST API
# ============================================================

async def extract_customer_data(
    client: httpx.AsyncClient,
    customer_api: str
) -> list[dict[str, Any]]:

    logger.info(
        "Calling customer API"
    )

    response = await client.get(
        customer_api,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):

        raise ValueError(
            "Customer API must return a JSON list"
        )

    return data


# ============================================================
# 5. ASYNC EXTRACTION
# ============================================================

async def extract_sources(
    config: Config
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]]
]:

    local_task = asyncio.to_thread(
        extract_orders_from_file,
        config.input_path
    )

    async with httpx.AsyncClient() as client:

        customer_task = extract_customer_data(
            client,
            config.customer_api
        )

        orders, customers = await asyncio.gather(
            local_task,
            customer_task
        )

    logger.info(
        "Orders: %d | Customers: %d",
        len(orders),
        len(customers)
    )

    return orders, customers


# ============================================================
# 6. TEXT CLEANING
# ============================================================

def clean_name(name: str) -> str:

    name = re.sub(
        r"\s+",
        " ",
        str(name)
    )

    return name.strip().title()


def clean_email(email: str) -> str:

    return (
        str(email)
        .strip()
        .lower()
    )


def clean_city(city: str) -> str:

    city = re.sub(
        r"[^A-Za-z ]",
        "",
        str(city)
    )

    return city.strip().title()


# ============================================================
# 7. FUNCTOOLS — BUSINESS LOGIC CACHE
# ============================================================

@functools.lru_cache(
    maxsize=256
)
def calculate_tax(
    subtotal: float
) -> float:

    return round(
        subtotal * 0.18,
        2
    )


@functools.lru_cache(
    maxsize=256
)
def classify_order(
    total: float
) -> str:

    if total >= 10000:
        return "PREMIUM"

    if total >= 5000:
        return "HIGH"

    if total >= 1000:
        return "MEDIUM"

    return "STANDARD"


# ============================================================
# 8. MATH — NUMERICAL TRANSFORMATION
# ============================================================

def calculate_shipping(
    quantity: int
) -> float:

    packages = math.ceil(
        quantity / 5
    )

    return packages * 50.0


# ============================================================
# 9. TRANSFORMATION
# ============================================================

def transform_order(
    order: dict[str, Any],
    customer_lookup: dict[int, dict[str, Any]]
) -> Order:

    customer_id = int(
        order["customer_id"]
    )

    customer = customer_lookup.get(
        customer_id
    )

    if customer is None:

        raise ValueError(
            f"Customer {customer_id} not found"
        )

    quantity = int(
        order["quantity"]
    )

    unit_price = float(
        order["unit_price"]
    )

    subtotal = round(
        quantity * unit_price,
        2
    )

    tax = calculate_tax(
        subtotal
    )

    shipping = calculate_shipping(
        quantity
    )

    total = round(
        subtotal +
        tax +
        shipping,
        2
    )

    return Order(

        order_id=int(
            order["order_id"]
        ),

        customer_id=customer_id,

        customer_name=clean_name(
            customer["name"]
        ),

        email=clean_email(
            customer["email"]
        ),

        city=clean_city(
            customer["city"]
        ),

        quantity=quantity,

        unit_price=unit_price,

        subtotal=subtotal,

        tax=tax,

        shipping=shipping,

        total=total,

        category=classify_order(
            total
        ),

        processed_at=datetime.now(
            timezone.utc
        ).isoformat()
    )


# ============================================================
# 10. MULTIPROCESSING
# ============================================================

def transform_chunk(
    args: tuple[
        list[dict[str, Any]],
        dict[int, dict[str, Any]]
    ]
) -> list[Order]:

    orders, customer_lookup = args

    return [
        transform_order(
            order,
            customer_lookup
        )

        for order in orders
    ]


def parallel_transform(
    orders: list[dict[str, Any]],
    customer_lookup: dict[int, dict[str, Any]]
) -> list[Order]:

    if not orders:
        return []

    workers = min(
        multiprocessing.cpu_count(),
        4
    )

    chunk_size = max(
        1,
        math.ceil(
            len(orders) / workers
        )
    )

    chunks = [
        orders[i:i + chunk_size]

        for i in range(
            0,
            len(orders),
            chunk_size
        )
    ]

    arguments = [
        (chunk, customer_lookup)

        for chunk in chunks
    ]

    logger.info(
        "Starting %d transformation workers",
        workers
    )

    with multiprocessing.Pool(
        processes=workers
    ) as pool:

        results = pool.map(
            transform_chunk,
            arguments
        )

    return list(
        itertools.chain.from_iterable(
            results
        )
    )


# ============================================================
# 11. VALIDATION
# ============================================================

def validate_orders(
    orders: list[Order]
) -> list[Order]:

    valid = []

    for order in orders:

        if not order.get("order_id"):

            logger.warning(
                "Missing order ID"
            )

            continue

        if not order.get("email"):

            logger.warning(
                "Missing email: %s",
                order["order_id"]
            )

            continue

        if order["quantity"] <= 0:

            logger.warning(
                "Invalid quantity: %s",
                order["order_id"]
            )

            continue

        if order["unit_price"] < 0:

            logger.warning(
                "Invalid price: %s",
                order["order_id"]
            )

            continue

        valid.append(order)

    return valid


# ============================================================
# 12. DEDUPLICATION
# ============================================================

def deduplicate_orders(
    orders: list[Order]
) -> list[Order]:

    seen = set()

    unique = []

    for order in orders:

        order_id = order["order_id"]

        if order_id in seen:

            logger.warning(
                "Duplicate order: %s",
                order_id
            )

            continue

        seen.add(order_id)

        unique.append(order)

    return unique


# ============================================================
# 13. COLLECTIONS — ANALYTICS
# ============================================================

def build_summary(
    orders: list[Order]
) -> dict[str, Any]:

    city_counts = Counter(
        order["city"]
        for order in orders
    )

    category_counts = Counter(
        order["category"]
        for order in orders
    )

    customer_totals = defaultdict(
        float
    )

    for order in orders:

        customer_totals[
            order["customer_id"]
        ] += order["total"]

    return {

        "order_count": len(orders),

        "city_counts": dict(
            city_counts
        ),

        "category_counts": dict(
            category_counts
        ),

        "customer_totals": dict(
            customer_totals
        )
    }


# ============================================================
# 14. ITERTOOLS — GROUPING
# ============================================================

def group_by_category(
    orders: list[Order]
) -> dict[str, list[Order]]:

    sorted_orders = sorted(
        orders,
        key=lambda order:
            order["category"]
    )

    groups = {}

    for category, group in itertools.groupby(
        sorted_orders,
        key=lambda order:
            order["category"]
    ):

        groups[category] = list(
            group
        )

    return groups


# ============================================================
# 15. LOCAL SINK
# ============================================================

def write_local_sink(
    orders: list[Order],
    summary: dict[str, Any],
    output_path: Path
) -> None:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    payload = {

        "metadata": {

            "generated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "record_count":
                len(orders)
        },

        "summary": summary,

        "orders": orders
    }

    temporary_path = output_path.with_suffix(
        ".tmp"
    )

    with temporary_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            payload,
            file,
            indent=2
        )

    # Atomic replacement
    temporary_path.replace(
        output_path
    )

    logger.info(
        "Local sink created: %s",
        output_path
    )


# ============================================================
# 16. AWS S3 SINK
# ============================================================

def upload_to_s3(
    output_path: Path,
    bucket: str,
    key: str
) -> None:

    logger.info(
        "Uploading to S3"
    )

    s3 = boto3.client(
        "s3"
    )

    s3.upload_file(
        str(output_path),
        bucket,
        key
    )

    logger.info(
        "S3 upload completed"
    )


# ============================================================
# 17. THREADING — OUTPUT VERIFICATION
# ============================================================

def verify_output(
    output_path: Path
) -> None:

    logger.info(
        "Verifying output"
    )

    if not output_path.exists():

        raise FileNotFoundError(
            "Output file missing"
        )

    with output_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if "orders" not in data:

        raise ValueError(
            "orders section missing"
        )

    if "summary" not in data:

        raise ValueError(
            "summary section missing"
        )

    logger.info(
        "Output verification successful"
    )


def run_verification_thread(
    output_path: Path
) -> None:

    thread = threading.Thread(
        target=verify_output,
        args=(output_path,),
        name="output-verifier"
    )

    thread.start()

    thread.join()


# ============================================================
# 18. SUBPROCESS — RUNTIME CHECK
# ============================================================

def runtime_check() -> None:

    result = subprocess.run(

        [
            sys.executable,
            "--version"
        ],

        capture_output=True,

        text=True,

        check=True
    )

    logger.info(
        "Python runtime: %s",
        result.stdout.strip()
    )


# ============================================================
# 19. OS — ENVIRONMENT
# ============================================================

def load_environment() -> dict[str, str]:

    return {

        "environment":
            os.getenv(
                "PIPELINE_ENV",
                "development"
            ),

        "region":
            os.getenv(
                "AWS_REGION",
                "ap-south-1"
            )
    }


# ============================================================
# 20. ORCHESTRATOR
# ============================================================

async def run_pipeline(
    config: Config
) -> None:

    start_time = datetime.now(
        timezone.utc
    )

    logger.info(
        "========== PIPELINE START =========="
    )

    environment = load_environment()

    logger.info(
        "Environment: %s",
        environment["environment"]
    )

    # Runtime verification
    runtime_check()

    # --------------------------------------------------------
    # EXTRACT
    # --------------------------------------------------------

    orders, customers = await extract_sources(
        config
    )

    # --------------------------------------------------------
    # CREATE LOOKUP
    # --------------------------------------------------------

    customer_lookup = {

        int(customer["id"]):
            customer

        for customer in customers
    }

    # --------------------------------------------------------
    # TRANSFORM
    # --------------------------------------------------------

    transformed = parallel_transform(
        orders,
        customer_lookup
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    validated = validate_orders(
        transformed
    )

    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------

    unique_orders = deduplicate_orders(
        validated
    )

    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    summary = build_summary(
        unique_orders
    )

    grouped = group_by_category(
        unique_orders
    )

    summary["groups"] = {
        category: len(records)

        for category, records
        in grouped.items()
    }

    # --------------------------------------------------------
    # LOCAL SINK
    # --------------------------------------------------------

    write_local_sink(
        unique_orders,
        summary,
        config.output_path
    )

    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    run_verification_thread(
        config.output_path
    )

    # --------------------------------------------------------
    # S3 SINK
    # --------------------------------------------------------

    if (
        config.s3_bucket
        and config.s3_key
    ):

        upload_to_s3(
            config.output_path,
            config.s3_bucket,
            config.s3_key
        )

    elapsed = (
        datetime.now(
            timezone.utc
        )
        - start_time
    )

    logger.info(
        "Processed orders: %d",
        len(unique_orders)
    )

    logger.info(
        "Elapsed: %s",
        elapsed
    )

    logger.info(
        "========== PIPELINE SUCCESS =========="
    )


# ============================================================
# CLI
# ============================================================

def get_argument(
    flag: str,
    default: str | None = None
) -> str | None:

    if flag not in sys.argv:

        return default

    index = sys.argv.index(
        flag
    )

    if index + 1 >= len(sys.argv):

        raise ValueError(
            f"Missing value for {flag}"
        )

    return sys.argv[index + 1]


def main() -> None:

    configure_logging()

    try:

        config = Config(

            input_path=Path(
                get_argument(
                    "--input",
                    "data/orders.json"
                )
            ),

            output_path=Path(
                get_argument(
                    "--output",
                    "output/orders.json"
                )
            ),

            customer_api=get_argument(
                "--customer-api"
            ),

            s3_bucket=get_argument(
                "--bucket"
            ),

            s3_key=get_argument(
                "--key"
            )
        )

        asyncio.run(
            run_pipeline(config)
        )

    except Exception:

        logger.exception(
            "PIPELINE FAILED"
        )

        raise


if __name__ == "__main__":

    main()