# json - dataengineering format
import json
student = { "id": 101,"name": "Ravi","marks": 85}
with open("student.json", "w") as file:
    json.dump(student, file, indent=4)
with open("student.json", "r") as file:
    data = json.load(file)
print(data)

#asyncio
import asyncio
async def task():
    print("Task started")

    await asyncio.sleep(2)

    print("Task completed")

asyncio.run(task())
#multiprocessing
from multiprocessing import Process

def calculate_square(number):
    print("Square:", number * number)

process = Process(target=calculate_square, args=(10,))

process.start()
process.join()

print("Process completed")
# treading
import threading

def print_numbers():
    for i in range(1, 6):
        print(i)

thread = threading.Thread(target=print_numbers)

thread.start()
thread.join()

print("Thread completed")