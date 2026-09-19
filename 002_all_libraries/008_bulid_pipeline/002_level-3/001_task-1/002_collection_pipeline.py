from collections import defaultdict, Counter
import json
students = [
    {"name": "Raj", "city": "HYD"},
    {"name": "Alice", "city": "DEL"},
    {"name": "Bob", "city": "HYD"},
    {"name": "John", "city": "DEL"},
    {"name": "Sam", "city": "HYD"},
]
for student in students:
    city = student["city"]
    grouped_students = defaultdict(list)
    city_count = Counter()
    city_count[city] += 1
    grouped_students[city].append(student["name"])
    print(f"City: {city}, Count: {city_count[city]}, Students: {grouped_students[city]}")
