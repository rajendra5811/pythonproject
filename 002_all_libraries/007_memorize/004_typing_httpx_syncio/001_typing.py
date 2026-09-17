

"""typing"""
import typing
#36)Explain the purpose of:

#List : A list is a mutable, ordered collection of elements. It is used to store multiple items in a single variable.
#Dict : A dictionary is an unordered collection of key-value pairs. It is used to store data values like a map, which allows for fast retrieval based on keys.
#Optional : Optional is a type hint that indicates that a variable can either be of a specified type or None. It is used to signify that a value may or may not be present.
#Union : Union is a type hint that allows a variable to be one of several specified types. It is used when a variable can hold different types of values.
#Tuple : A tuple is an immutable, ordered collection of elements. It is used to group multiple items together, and its immutability makes it suitable for fixed collections of data.
#Any : Any is a type hint that indicates that a variable can be of any type.

"""
37Q)Write a function annotation for:

function receives list of integers
returns a dictionary mapping strings to integers
"""
import typing

def map_ints_to_str_counts(nums: typing.List[int]) -> typing.Dict[str, int]:
    """
    Takes a list of integers and returns a dictionary mapping
    string representations of those integers to their counts.
    """
    result: typing.Dict[str, int] = {}
    for n in nums:
        key = str(n)
        result[key] = result.get(key, 0) + 1
    return result
"""httpx, asyncio"""
import httpx, asyncio
"""
38Q)Write the shortest httpx program that:

sends a GET request
checks the response
reads JSON.
"""

response = httpx.get("https://example.com")
response.raise_for_status()
data = response.json()
print(data)

#39Q)
Explain:

HTTP request
      ↓
server
      ↓
HTTP response
      ↓
status code + headers + body

What do these mean?"""

response.status_code
response.json()
response.text
response.raise_for_status()

Q23 — asyncio FIRST PRINCIPLE

Explain the difference between:

normal synchronous execution
asyncio execution
threading
multiprocessing

Do not focus on syntax. Explain what is actually waiting/running.

Q24 — async handwritten

Write a minimal asynchronous function using:

async def
await
asyncio.sleep()

that prints:

Start
End

with a simulated 2-second I/O wait.

Q25 — gather

What does this do conceptually?

await asyncio.gather(task1(), task2(), task3())

Why can it be useful when calling APIs?

Q26 — API mini-program

Write an asynchronous program that makes three API calls concurrently using httpx.AsyncClient and asyncio.gather().

You don't need a real API URL; use:

https://example.com
PART E — boto3 / AWS S3
Q27–Q31

Q27 — boto3

Write code to create an S3 client.

Then explain what this represents:

boto3.client("s3")

Q28 — S3 retrieval

Write code to:

list buckets
list objects inside a bucket
upload a local file
download an S3 object.

Name the relevant methods.

Q29 — S3 FIRST PRINCIPLE

Explain this pipeline:

Local CSV
   ↓
boto3
   ↓
S3 raw/
   ↓
transform
   ↓
S3 processed/

Why is S3 commonly used as a data lake/storage layer?

Q30 — debugging

Your program says:

students.json uploaded successfully

but S3 shows:

students.json
Size: 0 bytes

List at least 4 possible causes.

Q31 — handwritten AWS mini-program

Write a short program that:

1. creates an S3 client
2. uploads students.json
3. lists objects under raw/
4. prints their keys

Use boto3.

PART F — SQL BEGINNER → ADVANCED
Q32–Q40

Assume:

employees
---------
employee_id
name
salary
department_id

departments
-----------
department_id
department_name

Q32 — SQL basics

Write SQL to retrieve:

name
salary

for employees whose salary is greater than 50000, ordered from highest salary to lowest.

Q33 — aggregation

Write SQL to find:

department_id
average salary
maximum salary
employee count

for each department.

Q34 — HAVING

Find departments where:

average salary > 60000

Explain why this condition belongs in HAVING rather than WHERE.

Q35 — INNER JOIN

Write SQL that displays:

employee name
department name
salary

using the two tables.

Q36 — LEFT JOIN

Explain the conceptual difference:

INNER JOIN
LEFT JOIN

Then write a query showing all departments, including departments with zero employees.

Q37 — subquery

Find employees whose salary is greater than the company average salary.

Use a subquery.

Q38 — CTE

Rewrite Q37 using a CTE:

WITH ...

Q39 — window function

For every employee, display:

name
department_id
salary
department salary rank

using DENSE_RANK().

Q40 — TOP-N PER GROUP

Find the top 2 highest-paid employees in every department.

You must use a window function.

PART G — SQLAlchemy Core
Q41–Q44

Q41 — Core foundation

Write SQLAlchemy Core code that creates:

students
---------
id INTEGER PRIMARY KEY
name STRING
age INTEGER

using:

create_engine
MetaData
Table
Column
Integer
String

Q42 — Core query

Write SQLAlchemy Core code to select students where:

age > 18

Q43 — Core JOIN

Given:

students
student_id
name
department_id

departments
department_id
department_name

write a SQLAlchemy Core query joining the tables.

Q44 — FIRST PRINCIPLE

Explain the difference between:

Python object
SQLAlchemy Table
database table
SQLAlchemy statement
SQL query

What does SQLAlchemy actually do between your Python code and the database?

PART H — SQLAlchemy ORM
Q45–Q50

Q45 — Declarative Base

Write the modern SQLAlchemy ORM definition for:

Student
---------
id
name
age

using:

DeclarativeBase
Mapped
mapped_column

Q46 — mapped_column

Explain the difference between:

id: Mapped[int]

and:

id: Mapped[int] = mapped_column(primary_key=True)

Why is mapped_column() important?

Q47 — relationship

Create:

Department 1 ──────── many Student

using:

relationship()
ForeignKey()
back_populates

Write both classes.

Q48 — composite key

Explain this concept:

student_id  PRIMARY KEY + FOREIGN KEY
subject_id  PRIMARY KEY + FOREIGN KEY

Why is this useful for a many-to-many relationship?

Q49 — secondary

Explain:

relationship(
    secondary=student_subject,
    back_populates="students"
)

What does secondary mean?

Draw the relationship mentally as:

Student
   |
   ↓
association table
   |
   ↓
Subject

Q50 — cascade

Explain what:

cascade="all, delete-orphan"

means.

When would you use it?

PART I — itertools, functools, subprocess
Q51–Q54

Q51 — itertools

Explain and give one use case for:

chain()
product()
combinations()
groupby()
islice()

Q52 — itertools coding

Given:

a = [1, 2]
b = [3, 4]

write code using itertools.chain() to produce:

1 2 3 4

Then use product() to produce all pairs.

Q53 — functools

Explain:

partial()
reduce()
lru_cache()
wraps()

Give one Data Engineering-related use case for each.

Q54 — subprocess

Write Python code that executes:

python transform.py

from another Python program.

Then explain the difference between:

subprocess.run()
subprocess.Popen()
PART J — Classes: Beginner → Advanced
Q55–Q59

Q55 — class fundamentals

Write a Student class with:

student_id
name
marks

and methods:

display()
is_passed()

Q56 — encapsulation

Modify the class so that marks cannot be directly changed to an invalid value below 0 or above 100.

Explain how your solution provides encapsulation.

Q57 — inheritance + overriding

Create:

Employee
   ↑
Manager

where both have:

calculate_salary()

but Manager overrides it.

Use super() somewhere in the implementation.

Q58 — polymorphism

Create:

CSVReader
JSONReader

Both should have:

read()

Write a function:

process(reader)

that works with either object without checking:

if type(...)

Explain why this is polymorphism.

Q59 — advanced class thinking

Explain the difference between:

instance method
@classmethod
@staticmethod
@property
__init__
__str__
__repr__

For each, explain what receives self/cls or neither.

PART K — threading + multiprocessing + multithreading
Q60–Q62

Q60 — threading

Write a program that creates two threads.

Each thread should print:

Task started
Task finished

Explain why threading is useful for I/O-bound Data Engineering workloads.

Q61 — multiprocessing

Explain the fundamental difference between:

thread
process

Then explain why multiprocessing can help CPU-bound Python work.

Q62 — choose the correct tool

For each situation, choose:

normal synchronous
threading
asyncio
multiprocessing

and explain why.

A. Download 10,000 files from S3.

B. Make 1,000 API requests.

C. Perform CPU-heavy transformation on 20 GB of data.

D. Run three simple sequential database queries where each depends on the previous result.

PART L — MASTER INTEGRATION / FIRST PRINCIPLES
Q63

You receive:

students.json

containing 100,000 student records.

Design the Python/Data Engineering pipeline:

INPUT
  ↓
?
  ↓
?
  ↓
?
  ↓
DATABASE

Your solution must use concepts from at least 8 of the topics you've been tested on.

Explain:

how you discover the file
how you read JSON
how you validate/clean records
how you handle logging
how you handle dates
how you deal with errors
how you load into a database
where concurrency could be useful
where AWS S3 could fit
which parts should not be made concurrent and why.

Then write a short pseudocode/program skeleton for the pipeline.