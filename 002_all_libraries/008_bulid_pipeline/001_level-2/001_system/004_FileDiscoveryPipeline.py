#File Discovery Pipeline
"""raw/
├── students.json
├── employees.json
├── sales.csv
├── customers.json
└── notes.txt 
Expected Output: INFO - Found: students.json
INFO - Found: employees.json
INFO - Found: customers.json
INFO - Found: sales.csv
INFO - Found: notes.txt"""
from pathlib import Path

# Define the path to the raw data directory
raw_data_path = Path("raw")
Path.mkdir(raw_data_path, exist_ok=True)  
if not Path.exists("raw"):
    print("Error: Could not create raw data directory")
create_sample_files = [
    "students.json",
    "employees.json",
    "sales.csv",
    "customers.json",
    "notes.txt"
]
for file in create_sample_files:
    (raw_data_path / file).touch()
# Iterate over all files in the raw data directory
for file in raw_data_path.iterdir():
    if file.is_file():
        print(f"INFO - Found: {file.name}")