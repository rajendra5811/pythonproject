from pathlib import Path
import json
import logging
from pathlib import Path
import json


def load_json(file_path):

    path = Path(file_path)

    if not path.exists():
        print("File does not exist")
        return None

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data


data = load_json("data/raw/students.json")

print(data)
print("Number of students:", len(data))