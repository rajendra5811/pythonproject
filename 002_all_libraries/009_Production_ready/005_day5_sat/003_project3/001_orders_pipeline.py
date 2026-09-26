
import argparse
import asyncio
import boto3
import functools
import httpx
import itertools
import json
import logging
import math
import multiprocessing
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
import sys
import threading
from typing import Any, Iterable

LOGGER = logging.getLogger("orders_pipeline")


# ----------------------------- CONFIG ---------------------------------

def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Production-style orders ELT pipeline")
    parser.add_argument("--input", default="data/orders.json")
    parser.add_argument("--output", default="output/processed_orders.json")
    parser.add_argument(
        "--customer-api",
        default=os.getenv("CUSTOMER_API_URL", "https://jsonplaceholder.typicode.com/users"),
    )
    parser.add_argument("--s3-bucket", default=os.getenv("S3_BUCKET"))
    parser.add_argument("--s3-key", default=os.getenv("S3_KEY", "orders/processed_orders.json"))
    return parser.parse_args()


# ----------------------------- SOURCE ---------------------------------

def load_json(path: Path) -> Any:
    """Read JSON from disk and fail loudly when the source is invalid."""
    if not path.exists():
        raise FileNotFoundError(f"Source file does not exist: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_orders(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    if not isinstance(payload, list):
        raise ValueError("orders.json must contain a JSON list")

    if not all(isinstance(row, dict) for row in payload):
        raise ValueError("Every order must be a JSON object")

    LOGGER.info("Loaded %d raw orders from %s", len(payload), path)
    return payload


async def fetch_customer(session: httpx.AsyncClient, url: str, customer_id: int) -> dict[str, Any]:
    response = await session.get(url, params={"id": customer_id}, timeout=10.0)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, list):
        return data[0] if data else {}
    return data if isinstance(data, dict) else {}


async def fetch_customers(customer_ids: Iterable[int], api_url: str) -> dict[int, dict[str, Any]]:
    unique_ids = sorted(set(customer_ids))
    async with httpx.AsyncClient() as session:
        tasks = [fetch_customer(session, api_url, cid) for cid in unique_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    customers: dict[int, dict[str, Any]] = {}
    for customer_id, result in zip(unique_ids, results):
        if isinstance(result, Exception):
            LOGGER.warning("Customer API failed for id=%s: %s", customer_id, result)
            continue
        customers[customer_id] = result

    LOGGER.info("Fetched %d/%d customers", len(customers), len(unique_ids))
    return customers


# ----------------------------- VALIDATION -------------------------------

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().lower()


def is_valid_order(order: dict[str, Any]) -> bool:
    required = {"order_id", "customer_id", "product", "quantity", "unit_price", "email"}
    if not required.issubset(order):
        return False

    if not isinstance(order["quantity"], int) or order["quantity"] <= 0:
        return False

    if not isinstance(order["unit_price"], (int, float)) or order["unit_price"] < 0:
        return False

    return bool(EMAIL_RE.match(normalize_email(order.get("email"))))


def deduplicate_orders(orders: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[Any] = set()
    clean: list[dict[str, Any]] = []

    for order in orders:
        order_id = order.get("order_id")
        if order_id in seen:
            LOGGER.warning("Duplicate order skipped: %s", order_id)
            continue
        seen.add(order_id)
        clean.append(order)

    return clean


# ----------------------------- TRANSFORM --------------------------------

@functools.lru_cache(maxsize=1024)
def calculate_discount(total: float) -> float:
    """Business rule: larger orders receive a larger discount."""
    if total >= 1000:
        return 0.15
    if total >= 500:
        return 0.10
    if total >= 250:
        return 0.05
    return 0.0


def enrich_order(order: dict[str, Any], customers: dict[int, dict[str, Any]]) -> dict[str, Any]:
    quantity = order["quantity"]
    unit_price = float(order["unit_price"])
    subtotal = quantity * unit_price

    discount_rate = calculate_discount(subtotal)
    discount = subtotal * discount_rate
    total = subtotal - discount

    customer = customers.get(order["customer_id"], {})

    return {
        **order,
        "email": normalize_email(order.get("email")),
        "customer_name": customer.get("name", "UNKNOWN"),
        "city": customer.get("address", {}).get("city", "UNKNOWN"),
        "subtotal": round(subtotal, 2),
        "discount_rate": discount_rate,
        "discount": round(discount, 2),
        "total": round(total, 2),
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def transform_chunk(
    chunk: list[dict[str, Any]],
    customers: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    valid = [row for row in chunk if is_valid_order(row)]
    return [enrich_order(row, customers) for row in valid]


def chunked(items: list[Any], size: int) -> Iterable[list[Any]]:
    for start in range(0, len(items), size):
        yield items[start:start + size]


def transform_parallel(
    orders: list[dict[str, Any]],
    customers: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    workers = min(max(multiprocessing.cpu_count() - 1, 1), 4)
    chunk_size = max(1, math.ceil(len(orders) / workers))
    chunks = list(chunked(orders, chunk_size))

    with multiprocessing.Pool(processes=workers) as pool:
        parts = pool.starmap(transform_chunk, [(chunk, customers) for chunk in chunks])

    return list(itertools.chain.from_iterable(parts))


# ----------------------------- ANALYTICS --------------------------------

def build_metrics(orders: list[dict[str, Any]]) -> dict[str, Any]:
    revenue_by_city: defaultdict[str, float] = defaultdict(float)
    product_counts: Counter[str] = Counter()

    for order in orders:
        revenue_by_city[order["city"]] += order["total"]
        product_counts[order["product"]] += order["quantity"]

    sorted_orders = sorted(orders, key=lambda row: row["city"])
    orders_by_city = {
        city: sum(1 for _ in group)
        for city, group in itertools.groupby(sorted_orders, key=lambda row: row["city"])
    }

    return {
        "total_orders": len(orders),
        "total_revenue": round(sum(row["total"] for row in orders), 2),
        "revenue_by_city": dict(revenue_by_city),
        "units_by_product": dict(product_counts),
        "orders_by_city": orders_by_city,
    }


# ----------------------------- SINK -------------------------------------

def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    temp_path.replace(path)
    LOGGER.info("Wrote output: %s", path)


def upload_to_s3(path: Path, bucket: str | None, key: str) -> None:
    if not bucket:
        LOGGER.info("S3_BUCKET not set; skipping S3 sink")
        return

    client = boto3.client("s3")
    client.upload_file(str(path), bucket, key)
    LOGGER.info("Uploaded %s to s3://%s/%s", path, bucket, key)


def verify_output(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Sink verification failed: {path}")

    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("Output must be a JSON object")

    LOGGER.info("Sink verification passed: %s", path)


def threaded_verify(path: Path) -> None:
    error: list[Exception] = []

    def worker() -> None:
        try:
            verify_output(path)
        except Exception as exc:
            error.append(exc)

    thread = threading.Thread(target=worker, name="sink-verifier")
    thread.start()
    thread.join()

    if error:
        raise error[0]


# ----------------------------- OPERATIONS --------------------------------

def python_runtime_check() -> None:
    result = subprocess.run(
        [sys.executable, "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    LOGGER.info("Runtime: %s", result.stdout.strip() or result.stderr.strip())


def run_pipeline(args: argparse.Namespace) -> None:
    started = datetime.now(timezone.utc)

    python_runtime_check()

    raw_orders = load_orders(Path(args.input))
    unique_orders = deduplicate_orders(raw_orders)

    customer_ids = [
        int(row["customer_id"])
        for row in unique_orders
        if isinstance(row.get("customer_id"), int)
    ]
    customers = asyncio.run(fetch_customers(customer_ids, args.customer_api))

    transformed = transform_parallel(unique_orders, customers)
    metrics = build_metrics(transformed)

    output_payload = {
        "pipeline": "orders_elt",
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "data": transformed,
        "metrics": metrics,
    }

    output_path = Path(args.output)
    atomic_write_json(output_path, output_payload)
    threaded_verify(output_path)
    upload_to_s3(output_path, args.s3_bucket, args.s3_key)

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    LOGGER.info(
        "Pipeline complete | raw=%d | unique=%d | valid=%d | elapsed=%.2fs",
        len(raw_orders),
        len(unique_orders),
        len(transformed),
        elapsed,
    )


if __name__ == "__main__":
    configure_logging()
    arguments = parse_args()

    try:
        run_pipeline(arguments)
    except Exception:
        LOGGER.exception("Pipeline failed")
        raise SystemExit(1)
