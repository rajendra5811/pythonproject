"""Python Libraries: json, datetime, re"""
#9 JSON
import json
student = {
    "id": 101,
    "name": "Raj",
    "marks": 92
}

#15Q)Write code to:
#a)convert it into a JSON string
json_string = json.dumps(student)
#b)save it to student.json
with open("student.json", "w") as f:
    json.dump(student, f)
#c)read it back
with open("student.json", "r") as f:
    student = json.load(f)
#d)convert it into a Python object.
student = json.loads(json_string)

#16Q)Name the four important JSON operations/functions involved.
json.dumps() #converts a Python object into a JSON string.
json.dump() #writes a Python object to a file in JSON format.
json.loads() #converts a JSON string into a Python object.
json.load() #reads a JSON file and converts it into a Python object.

"""datetime"""
import datetime
#17Q)Write code to:
# a) get current date/time
current_datetime = datetime.datetime.now()
# b) get today's date
today_date = datetime.date.today()
# c) format the current date as:
#    2026-09-16
formatted_date = current_datetime.strftime("%Y-%m-%d")

#18Q)Name the relevant methods.
datetime.datetime.now() #returns the current local date and time.
datetime.date.today() #returns the current local date.
datetime.strftime() #formats a datetime object as a string according to a specified format.

 
#19Q)What is the conceptual difference between:
#a)datetime: when both date and time are important.
#b)date: when only the date is important, without time information.
#c)timedelta: differences between two dates or times, representing a duration like "5 days" or "2 hours".

#20Q)Give one Data Engineering use case for each.
# datetime: Logging the exact timestamp of data ingestion events in a data pipeline.
# date: Storing the date of a user's last login in a database without needing the time.
# timedelta: Calculating the time difference between two events, such as the duration of a data