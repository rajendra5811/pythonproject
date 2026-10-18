import json
import math
import re
import logging

from pathlib import Path
from datetime import datetime
from collections import defaultdict


BASE_DIR = Path(__file__).parent

INPUT_FILE = BASE_DIR / "input" / "students.json"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def read_students():

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



def validate(student):

    if not re.fullmatch(
        r"STU\d{3}",
        student["student_id"]
    ):
        return False

    try:

        datetime.strptime(
            student["date"],
            "%Y-%m-%d"
        )

    except ValueError:

        return False

    if student["status"] not in {
        "present",
        "absent"
    }:
        return False

    if not 0 <= student["marks"] <= 100:
        return False

    return True


def transform(student):

    student["name"] = (
        " ".join(
            student["name"]
            .strip()
            .split()
        )
    )

    student["class_name"] = (
        student["class_name"]
        .strip()
        .upper()
    )

    return student


def aggregate(students):

    result = defaultdict(
        lambda: {
            "present": 0,
            "total": 0,
            "marks": []
        }
    )

    for student in students:

        sid = student["student_id"]

        result[sid]["total"] += 1

        if student["status"] == "present":
            result[sid]["present"] += 1

        result[sid]["marks"].append(
            student["marks"]
        )

    report = {}

    for sid, data in result.items():

        attendance = (
            data["present"]
            / data["total"]
        ) * 100

        report[sid] = {

            "attendance":
                math.floor(attendance),

            "average_marks":
                sum(data["marks"])
                / len(data["marks"])
        }

    return report



def write_report(report):

    output_file = (
        OUTPUT_DIR /
        "student_report.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )


def run_pipeline():

    logger.info(
        "Pipeline started"
    )

    students = read_students()

    valid_students = []

    for student in students:

        if validate(student):

            valid_students.append(
                transform(student)
            )

        else:

            logger.warning(
                "Rejected: %s",
                student.get("student_id")
            )

    report = aggregate(
        valid_students
    )

    write_report(report)

    logger.info(
        "Pipeline completed"
    )



if __name__ == "__main__":

    run_pipeline()