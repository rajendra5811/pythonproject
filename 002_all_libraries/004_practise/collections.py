from pathlib import Path
import re

email = "  RAJ@EXAMPLE.COM  "

email = email.strip().lower()

if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
    print("Valid email")

from collections import Counter

cities = [
    "Hyderabad",
    "Delhi",
    "Hyderabad",
    "Chennai",
    "Delhi",
    "Hyderabad"
]

cleaned = [re.sub(r"\s+", " ", city).strip() for city in cities]

counts = Counter(cleaned)

print(counts)