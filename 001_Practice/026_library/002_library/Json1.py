import json

student = { "id": 101,"name": "Ravi","marks": 85}
# write on student.json
with open("student.json", "w") as file:
    json.dump(student, file, indent=4)
#read student.json
with open("student.json", "r") as file:
    data = json.load(file)

print(data)