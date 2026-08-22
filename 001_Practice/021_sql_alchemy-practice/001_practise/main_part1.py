#operating system env (python foundation)
import os
current_dir = os.getcwd()
print("current_directory", current_dir)
#env variable
os.getenv("AWS_REGION")
#PATHLIB find path/file
from pathlib import Path
path = Path("data/raw/students.json")
# exists
path.exists()
path.name
path.stem
path.suffix
path.parent
# json read the data
import json

with open("students.json", "r") as file:
    students = json.load(file)
#type
type(students)
#json dump
with open("students_cleaned.json", "w") as file:
    json.dump(students, file, indent=4)
# sys command inputs
import sys

print(sys.argv)
print(sys.argv[1])
#typing
from typing import List, Dict, Any

def transform_students(
    students: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

  student_ids: List[int] = [101, 102, 103]

student: Dict[str, Any] = {
    "student_id": 101,
    "name": "Raj",
    "marks": 85
}
def transform_students(
    students: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

