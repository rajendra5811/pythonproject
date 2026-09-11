"""12Q)Given:

data/processed/students.json

Upload it to an S3 bucket."""
import boto3
import json
from pathlib import Path
import os

# Initialize the S3 client
s3 = boto3.client('s3')

# Read the JSON file
data_dir = "data/processed/"   
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"Directory '{data_dir}' created.")
else:
    print(f"Directory '{data_dir}' already exists.")
with open('data/processed/students.json', 'r') as f:
    data = json.load(f)

# Upload the JSON file to S3
s3.put_object(
    Bucket='your-bucket-name',
    Key='students.json',
    Body=json.dumps(data)
)

"""13)Create a worker that prints:

Processing students...

Start the thread and make the main program wait for it."""
import threading


def worker():
    print("Processing students...")


thread = threading.Thread(target=worker)

print("Starting worker thread...")
thread.start()

print("Waiting for worker thread...")
thread.join()

print("Worker thread completed.")

"""14)Create an async function that waits for 2 seconds and then prints:

Finished

Run it from normal Python code."""
import asyncio


async def print_finished():
    await asyncio.sleep(2)
    print("Finished")


# Run the async function
asyncio.run(print_finished())

""""Program 15 — multiprocessing + math

Calculate square roots:

[16, 25, 36, 49]

using multiple processes."""
import multiprocessing
import math

def calculate_square_root(number):
    return math.sqrt(number)

if __name__ == '__main__':
    numbers = [16, 25, 36, 49]
    with multiprocessing.Pool() as pool:
        results = pool.map(calculate_square_root, numbers)
        print(results)
