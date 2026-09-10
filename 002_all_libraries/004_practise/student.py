import os
import json
import Pathlib import Path
from datetime import datetime

print(os.getcwd()) # current directory
os.makedirs("students", exist_ok=True) # create a directory for students if it doesn't exist
path = Path("data/students.json") # create a Path object for the students file
with open(path, "r") as f: # open the students file in read mode
    students = json.load(f) # load the students data from the file
student ={"name": "John Doe",
           "age": 20, 
           "major": "Computer Science",
           "Processed_at": datetime.now().isoformat() }
json_string = json.drop(student)
          