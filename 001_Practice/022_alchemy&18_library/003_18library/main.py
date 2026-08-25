#os library
import os

path = os.getcwd()
print("Current directory:", path)

if not os.path.exists("data"):
    os.mkdir("data")
    print("data folder created")
else:
    print("data folder already exists")

# sys library
import os

path = os.getcwd()
print("Current directory:", path)

if not os.path.exists("data"):
    os.mkdir("data")
    print("data folder created")
else:
    print("data folder already exists")
# datetime library
from datetime import datetime, timedelta

today = datetime.now()

print("Today:", today)
print("After 7 days:", today + timedelta(days=7))
# Collections  library
from collections import Counter

data = ["IT", "HR", "IT", "Finance", "IT", "HR"]

counts = Counter(data)

print(counts)

employees = [
    ("IT", "Ravi"),
    ("HR", "Priya"),
    ("IT", "Arjun"),
    ("HR", "Sneha")
]
from collections import defaultdict

groups = defaultdict(list)

for department, name in employees:
    groups[department].append(name)

print(groups)

#6.itertools
a = [1, 2, 3]
b = [4, 5, 6]

from itertools import chain

result = chain(a, b)

print(list(result))
