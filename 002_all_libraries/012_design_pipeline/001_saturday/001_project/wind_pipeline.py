import json
import re
import math
from datetime import datetime
from pathlib import Path
from collections import defaultdict

INPUT = Path("wind_01.json")
OUTPUT = Path("wind_report.json")


def read_data():
    with INPUT.open() as f:
        return json.load(f)


def valid(r):
    return (
        re.fullmatch(r"WT\d{3}", r["turbine_id"])
        and r["wind_speed"] >= 0
        and r["generated_kwh"] >= 0
        and r["capacity_kw"] > 0
        and datetime.fromisoformat(r["timestamp"])
    )


def process(records):
    result = defaultdict(dict)

    for r in records:
        if not valid(r):
            continue

        turbine = r["turbine_id"]

        result[turbine] = {
            "farm": r["farm"].strip().upper(),
            "wind_speed": r["wind_speed"],
            "generated_kwh": r["generated_kwh"],
            "utilization": math.floor(
                r["generated_kwh"] /
                r["capacity_kw"] * 100
            )
        }

    return result


def save(data):
    with OUTPUT.open("w") as f:
        json.dump(data, f, indent=4)


def main():
    records = read_data()
    report = process(records)
    save(report)
    print("Pipeline completed")


if __name__ == "__main__":
    main()