import json

def load_json_file(file_path = "raw/students.json"):
    with open(file_path, "r") as f:
        return json.load(f)


    for data in students:
        print(data)
        print(students.name.strip(" "))