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
INPUT_FILE = BASE_DIR / "data" / "employees.json"
OUTPUT_DIR = BASE_DIR / "output"
DB_URL = os.getenv("EMPLOYEE_DB_URL", f"sqlite:///{BASE_DIR / 'employees.db'}")
WEBHOOK_URL = os.getenv("EMPLOYEE_WEBHOOK_URL", "https://httpbin.org/post")

Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    processed_at = Column(DateTime, nullable=False)


def setup():
    OUTPUT_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=OUTPUT_DIR / "employee_pipeline.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    Base.metadata.create_all(create_engine(DB_URL))


def extract() -> List[Dict[str, Any]]:
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)
    logging.info("Extracted %d employee records", len(records))
    return records


def validate(record: Dict[str, Any]) -> tuple:
    pattern = re.compile(r"^[A-Za-z0-9_-]+$")
    employee_id, name = record.get("employee_id"), record.get("name")
    department, salary = record.get("department"), record.get("salary")
    status = record.get("status", "ACTIVE")

    if not employee_id or not pattern.match(str(employee_id)):
        return record, "Invalid or missing employee_id"
    if not name or len(str(name).strip()) < 2:
        return record, "Invalid or missing name"
    if not department or not pattern.match(str(department)):
        return record, "Invalid or missing department"
    if not isinstance(salary, (int, float)) or salary <= 0 or math.isnan(salary):
        return record, "Salary must be a positive number"
    if status not in {"ACTIVE", "INACTIVE", "ON_LEAVE"}:
        return record, "Invalid status"
    return record, None


def transform(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "employee_id": str(record["employee_id"]).upper(),
        "name": str(record["name"]).strip().title(),
        "department": str(record["department"]).strip().upper(),
        "salary": round(float(record["salary"]), 2),
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


def load_employees(records: List[Dict[str, Any]]) -> int:
    engine = create_engine(DB_URL)
    session = sessionmaker(bind=engine)()
    loaded = 0
    try:
        for record in records:
            employee = session.query(Employee).filter_by(employee_id=record["employee_id"]).first()
            if employee:
                for key, value in record.items():
                    setattr(employee, key, value)
            else:
                session.add(Employee(**record))
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
            response = await client.post(WEBHOOK_URL, json=summary)
            logging.info("Webhook status: %s", response.status_code)
    except httpx.HTTPError as error:
        logging.warning("Webhook failed: %s", error)


def export_report(summary: Dict[str, Any]) -> Path:
    output_file = OUTPUT_DIR / "employee_summary.json"
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
    loaded_count = load_employees(valid)

    departments = defaultdict(list)
    for employee in valid:
        departments[employee["department"]].append(employee["salary"])

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_count": len(records),
        "valid_count": len(valid),
        "loaded_count": loaded_count,
        "rejected_count": len(rejected),
        "department_summary": {
            department: {
                "employee_count": len(salaries),
                "total_salary": round(sum(salaries), 2),
                "average_salary": round(sum(salaries) / len(salaries), 2),
                "highest_salary": max(salaries),
            }
            for department, salaries in departments.items()
        },
        "status_summary": dict(Counter(employee["status"] for employee in valid)),
        "rejection_reasons": dict(Counter(item["error"] for item in rejected)),
        "rejected_records": [
            {"employee_id": item["record"].get("employee_id"), "error": item["error"]}
            for item in rejected[:10]
        ],
    }

    export_report(summary)
    threading.Thread(target=lambda: asyncio.run(notify(summary)), daemon=True).start()

    if os.getenv("EMPLOYEE_POST_COMMAND"):
        subprocess.run([sys.executable, "-c", os.environ["EMPLOYEE_POST_COMMAND"]], check=False)

    logging.info("Employee pipeline completed: %s", summary["valid_count"])
    return summary


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=4, default=str))