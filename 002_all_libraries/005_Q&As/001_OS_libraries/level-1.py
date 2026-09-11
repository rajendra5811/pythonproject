"""1Q)Write a program that:

prints the current directory
creates a directory called data
checks whether data exists"""
import os
print("Current directory:", os.getcwd())
data_dir = "data"   
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"Directory '{data_dir}' created.")
else:
    print(f"Directory '{data_dir}' already exists.")

"""2Q)Write a program using Path.

Then print:

filename
extension
parent directory"""

from pathlib import Path

file_path = Path("data/students.json")
print("Filename:", file_path.name)
print("Extension:", file_path.suffix)
print("Parent directory:", file_path.parent)

"""3Q)student = {
    "id": 101,
    "name": "Raj",
    "marks": 85
}

Write the program to:

Convert Python dictionary → JSON string
Convert JSON string → Python dictionary
Print the result"""
import json

student = {
    "id": 101,
    "name": "Raj",
    "marks": 85
}

json_string = json.dumps(student)
print("JSON string:", json_string)

parsed_student = json.loads(json_string)
print("Parsed student:", parsed_student)
"""4Q) — datetime

Create the current timestamp and print it in:

2026-09-11 18:30:00

format."""
import datetime

current_timestamp = datetime.datetime.now()
print("Current timestamp:", 
      current_timestamp.strftime("%Y-%m-%d %H:%M:%S"))

"""5Q) giventext = "Student123 scored 95"

Replace every digit with:

X"""
import re

giventext = "Student123 scored 95"
result = re.sub(r'\d', 'X', giventext)
print("Result:", result)

"""6Q) Given:

cities = [
    "Hyderabad",
    "Delhi",
    "Hyderabad",
    "Pune",
    "Delhi",
    "Hyderabad"
]

Use Counter to produce:

Hyderabad → 3
Delhi → 2
Pune → 1"""
from collections import Counter
cities = [ "Hyderabad","Delhi","Hyderabad","Pune","Delhi","Hyderabad"
]

city_counts = Counter(cities)
for city, count in city_counts.items():
    print(f"{city} → {count}")

