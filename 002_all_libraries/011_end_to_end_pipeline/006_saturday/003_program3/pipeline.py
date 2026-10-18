import asyncio, json, logging, math, os, re, subprocess, sys, threading
from collections import Counter, defaultdict
from datetime import datetime
from functools import reduce
from itertools import groupby
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List

import httpx
from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "records.json"
OUTPUT_DIR = BASE_DIR / "output"
DB_URL = os.getenv("PIPELINE_DB_URL", f"sqlite:///{BASE_DIR / 'pipeline.db'}")
API_URL = os.getenv("PIPELINE_API_URL", "https://httpbin.org/post")

Base = declarative_base()


class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    processed_at = Column(DateTime, nullable=False)


def setup():
    OUTPUT_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=OUTPUT_DIR / "pipeline.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    Base.metadata.create_all(create_engine(DB_URL))


def extract() -> List[Dict[str, Any]]:
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)
    logging.info("Extracted %d records", len(records))
    return records


def validate(record: Dict[str, Any]) -> tuple:
    pattern = re.compile(r"^[A-Za-z0-9_-]+$")
    record_id, category = record.get("record_id"), record.get("category")
    value, status = record.get("value"), record.get("status", "ACTIVE")

    if not record_id or not pattern.match(str(record_id)):
        return record, "Invalid or missing record_id"
    if not category or not pattern.match(str(category)):
        return record, "Invalid or missing category"
    if not isinstance(value, (int, float)) or value < 0 or math.isnan(value):
        return record, "Invalid value"
    if status not in {"ACTIVE", "INACTIVE"}:
        return record, "Invalid status"
    return record, None


def transform(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "record_id": str(record["record_id"]),
        "category": str(record["category"]).upper(),
        "value": round(float(record["value"]), 2),
        "status": record["status"],
        "processed_at": datetime.now(),
    }


def process_batch(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid, rejected = [], []
    for record in batch:
        record, error = validate(record)
        (rejected.append({"record": record, "error": error}) if error
         else valid.append(transform(record)))
    return {"valid": valid, "rejected": rejected}


def load_records(records: List[Dict[str, Any]]) -> int:
    engine = create_engine(DB_URL)
    session = sessionmaker(bind=engine)()
    loaded = 0
    try:
        for record in records:
            exists = session.query(Record).filter_by(record_id=record["record_id"]).first()
            if exists:
                for key, value in record.items():
                    setattr(exists, key, value)
            else:
                session.add(Record(**record))
            loaded += 1
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return loaded


async def notify(summary: Dict[str, Any]) -> None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(API_URL, json=summary)
            logging.info("Notification status: %s", response.status_code)
    except httpx.HTTPError as error:
        logging.warning("Notification failed: %s", error)


def export_report(summary: Dict[str, Any]) -> Path:
    output_file = OUTPUT_DIR / "pipeline_summary.json"
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, default=str)
    return output_file


def run_pipeline(batch_size: int = 100, workers: int = 4) -> Dict[str, Any]:
    setup()
    records = extract()
    batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]

    with Pool(processes=min(workers, len(batches) or 1)) as pool:
        results = pool.map(process_batch, batches)

    valid = reduce(lambda a, b: a + b, [result["valid"] for result in results], [])
    rejected = reduce(lambda a, b: a + b, [result["rejected"] for result in results], [])

    loaded_count = load_records(valid)

    categories = defaultdict(list)
    for record in valid:
        categories[record["category"]].append(record["value"])

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_count": len(records),
        "valid_count": len(valid),
        "loaded_count": loaded_count,
        "rejected_count": len(rejected),
        "category_summary": {
            category: {
                "count": len(values),
                "total": round(sum(values), 2),
                "average": round(sum(values) / len(values), 2),
                "maximum": max(values),
            }
            for category, values in categories.items()
        },
        "rejection_reasons": dict(Counter(item["error"] for item in rejected)),
        "top_rejections": [
            {"record": item["record"].get("record_id"), "error": item["error"]}
            for item in rejected[:10]
        ],
    }

    export_report(summary)
    threading.Thread(target=lambda: asyncio.run(notify(summary)), daemon=True).start()

    if os.getenv("PIPELINE_RUN_COMMAND"):
        subprocess.run(sys.executable.split() + ["-c", os.environ["PIPELINE_RUN_COMMAND"]], check=False)

    logging.info("Pipeline completed: %s", summary["valid_count"])
    return summary


if __name__ == "__main__":
    result = run_pipeline()
    print(json.dumps(result, indent=4, default=str))