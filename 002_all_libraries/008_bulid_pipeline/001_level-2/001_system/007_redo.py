import json
from pathlib import Path

file_path = Path("raw/students.json")
with open(file_path) as f:
    data = json.loads(f.read())
#stores it in students
students = data
for student in students:
    print(data)
    print(student.get("name").strip(''))
