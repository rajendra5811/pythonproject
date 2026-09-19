import json
from pathlib import Path
import re
Path.mkdir("raw_data", exist_ok=True)
save_path = Path("raw_data/students.json")
students = [
    " Raj123 ",
    " Alice45 ",
    " Bob "
]

# Save the raw data
with open(save_path, "w") as f:
    json.dump(students, f)

#Create a cleaning pipeline:
cleaning_pipeline = [
    lambda x: x.strip(),
    lambda x: ''.join(c for c in x if not c.isdigit())
]

# Apply the cleaning pipeline to each student
cleaned_students = [cleaning_pipeline[0](student) for student in students]
cleaned_students = [cleaning_pipeline[1](student) for student in cleaned_students]

# Save the cleaned data
with open(Path("raw_data/cleaned_students.json"), "w") as f:
    json.dump(cleaned_students, f)

#Apply the cleaning pipeline to each student
for step in cleaning_pipeline:
    students = [step(student) for student in students]

# Save the cleaned data
with open(Path("raw_data/cleaned_students.json"), "w") as f:
    json.dump(students, f)

#Create a cleaning pipeline: took help for lambda
cleaning_pipeline = [
    lambda x: re.sub(r'\d+', '', x),
    lambda x: x.strip()
]

# Apply the cleaning pipeline to each student
for level in cleaning_pipeline:
    students = [level(student) for student in students]

# Save the cleaned data
with open(Path("raw_data/cleaned_students.json"), "w") as f:
    json.dump(students, f)

with open(Path("raw_data/cleaned_students.json"), "r") as f:
    cleaned_students = json.load(f)
for student in cleaned_students:
    print(student)
