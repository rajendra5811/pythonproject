import subprocess

result = subprocess.run(
    ["python", "--version"],
    capture_output=True,
    text=True
)

# math
import math

math.ceil(10.2)
math.floor(10.8)

#islice
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, MappedColumn, sessionmaker 
from itertools import islice

rows = session.execute(query)

first_100 = islice(rows, 100)

#collection
from collections import Counter

grades = ["A", "A", "B", "A", "C"]

print(Counter(grades))