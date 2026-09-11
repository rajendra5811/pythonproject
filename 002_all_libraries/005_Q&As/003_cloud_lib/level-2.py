# 2 libraies
"""7)given data/students.json

and print the loaded Python data."""
import json
from pathlib import Path

# Load the JSON file
file_path = Path("data/students.json")
with open(file_path, "r") as f:
    data = json.load(f)

# Print the loaded Python data
print(data)

"""8)Given:

cities = [
    " Hyderabad ",
    "HYDERABAD",
    " Delhi ",
    "Delhi"
]

Clean the city names so that:

Hyderabad
Hyderabad
Delhi
Delhi

Then count them using Counter."""
from collections import Counter
import re

cities = [
    " Hyderabad ",
    "HYDERABAD",
    " Delhi ",
    "Delhi"
]

# Clean the city names
cleaned_cities = [re.sub(r'^\s+|\s+$', '', city).lower() for city in cities]

# Count the cleaned city names
city_counts = Counter(cleaned_cities)

print(city_counts)

"""9)Given:student = {
    "id": 101,
    "name": "Raj",
    "marks": 90
}

Add:

processed_at

with the current timestamp.

Then convert the entire dictionary to a JSON string."""
import json
from datetime import datetime

student = {
    "id": 101,
    "name": "Raj",
    "marks": 90
}

# Add processed_at with the current timestamp
student["processed_at"] = datetime.now().isoformat()

# Convert the entire dictionary to a JSON string
json_string = json.dumps(student)

print(json_string)

"""10)Given: https://api.example.com/students

and:

Make GET request
Check status code
Parse JSON response
Print the data"""
import httpx
import json

# Make GET request
response = httpx.get("https://api.example.com/students")

# Check status code
if response.status_code == 200:
    # Parse JSON response
    data = response.json()
    # Print the data
    print(data)
else:
    print(f"Error: {response.status_code}")

"""11)httpx + logging

Write a program that makes an API request.

If successful:

INFO: Student API request successful

If it fails:

ERROR: Student API request failed"""
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO) 

# Make API request
try:
    response = httpx.get("https://api.example.com/students")
    if response.status_code == 200:
        logging.info("Student API request successful")
    else:
        logging.error("Student API request failed")
except Exception as e:
    logging.error(f"Student API request failed: {e}")