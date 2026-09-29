import os
import json
import re

from pathlib import Path
from datetime import datetime
from collections import Counter


# 1. Create output directory
os.makedirs("data/processed", exist_ok=True)


# 2. Create paths
input_file = Path("data/raw/students.json")
output_file = Path("data/processed/students_clean.json")


# 3. Read JSON
with input_file.open("r") as file:
    students = json.load(file)


# 4. Prepare city list
cities = []


# 5. Transform students
for student in students:

    # Clean name
    student["name"] = re.sub(
        r"\s+",
        " ",
        student["name"]
    ).strip()

    # Clean city
    student["city"] = re.sub(
        r"\s+",
        " ",
        student["city"]
    ).strip()

    # Clean email
    student["email"] = student["email"].strip().lower()

    # Add timestamp
    student["processed_at"] = datetime.now().isoformat()

    # Collect city
    cities.append(student["city"])


# 6. Count cities
city_counts = Counter(cities)


# 7. Save JSON
with output_file.open("w") as file:
    json.dump(students, file, indent=2)


# 8. Verify output
print("City counts:", city_counts)
print("Output exists:", os.path.exists(output_file))