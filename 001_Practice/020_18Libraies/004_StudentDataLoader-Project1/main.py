#1. Finds the current working directory.
import os
path_dir = os.getcwd()
print("the directory", path_dir)

#2. Checks whether data exists.
if os.path.exists(courses.json):
    print("exists")
       
#3. Checks whether processed exists.
if os.path.exists(courses.json):
   os.mkdir("processed")

#4. Creates missing directories.
if os.path.exists(courses.json):
    os.makedir(course.json)

# 5. Finds all .json files in data.
6. Prints their full paths.
dir_list()
7. Reads DATABASE_URL from the environment.
engine = create_engine(DATABASE_URL)
DATABASE_URL = os
os.getenv(DATABASE_URL)

import os
import json
from pathlib import Path


# 1. Find current working directory
current_directory = os.________()
print("Current directory:", current_directory)


# 2. Check data directory
if os.path.________("data"):
    print("Data folder exists")
else:
    print("Data folder does not exist")


# 3. Create processed directory if missing
if ______ os.path.exists("processed"):
    os.________("processed")
    print("Processed folder created")
else:
    print("Processed folder already exists")


# 4. Find JSON files
data_path = Path("data")
json_files = data_path.________("*.json")


# 5. Print JSON files
print("\nJSON files:")
for file in __________:
    print(file.________())


# 6. Student file
students_file = Path("data") / "________"


# 7. Check student file
if students_file.________():
    print("\nStudents file found")

    with open(students_file, "r") as file:
        students = json.________(file)

else:
    print("\nStudents file not found")
    students = []


# 8. Course file
courses_file = Path("data") / "________"


# 9. Check course file
if courses_file.________():
    print("Courses file found")

    with open(courses_file, "r") as file:
        courses = json.________(file)

else:
    print("Courses file not found")
    courses = []


# 10. Count records
print("\nNumber of students:", ________(students))
print("Number of courses:", ________(courses))


# 11. Display students
print("\nStudents:")
for student in students:
    print(
        student["________"],
        student["________"]
    )


# 12. Display courses
print("\nCourses:")
for course in courses:
    print(
        course["________"],
        course["________"]
    )


# 13. Environment variable
database_url = os.getenv("________________")


# 14. Final report
print("\n==============================")
print("STUDENT DATA REPORT")
print("==============================")
print("Students:", len(students))
print("Courses:", len(courses))

if database_url:
    print("Database configuration: Found")
else:
    print("Database configuration: Not Found")