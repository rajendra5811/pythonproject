

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

"""39Q)
Explain:

HTTP request : client for a web page  typically using methods like GET, POST, PUT, DELETE, etc.
      ↓
server : recieves and sends back a response like page content, data, or status codes
      ↓
HTTP response: the server's reply to the client's request, containing a status code, headers, and a body.
      ↓
status code + headers + body 

What do these mean?"""

response.status_code
response.json()
response.text
response.raise_for_status()

""" asyncio FIRST PRINCIPLE
40Q)
Explain the difference between:

normal synchronous execution : In normal synchronous execution, each operation must complete before the next one begins. This means that if an operation involves I/O (like a network request), the program will wait for it to finish before moving on to the next task.

asyncio execution: In asyncio execution, multiple operations can be scheduled to run concurrently, but they are not truly running in parallel. Instead, they are managed by an event loop that switches between them as needed, allowing for efficient handling of I/O-bound tasks.

threading: Threading allows for true parallelism in CPU-bound tasks by creating separate threads that can run simultaneously on different CPU cores. However, due to Python's Global Interpreter Lock (GIL), only one thread can execute Python code at a time.

multiprocessing: Multiprocessing creates separate processes, each with their own Python interpreter and memory space. This allows for true parallelism in CPU-bound tasks, as each process can run on a different CPU core.

Do not focus on syntax. Explain what is actually waiting/running."""
# waiting: In normal synchronous execution, the program waits for each operation to complete before moving on. 
# In asyncio, the event loop manages multiple tasks, allowing them to yield control when they are waiting for I/O, so other tasks can run. In threading, threads can run concurrently, but due to the GIL, only one thread executes Python code at a time. In multiprocessing, separate processes run independently, allowing for true parallel execution.
# running: In normal synchronous execution, only one operation runs at a time. In asyncio,

""" 41Q)
Write a minimal asynchronous function using:

async def
await
asyncio.sleep()

that prints:

Start
End

with a simulated 2-second I/O wait.
"""


async def print_values():
    print("Start")
    await asyncio.sleep(2)
    print("End")

# Run the asynchronous function
asyncio.run(print_values())   
"""
42Q)
What does this do conceptually?

await asyncio.gather(task1(), task2(), task3())

Why can it be useful when calling APIs?"""
#await asyncio.gather(task1(), task2(), task3()) conceptually allows multiple asynchronous tasks (task1, task2, and task3) to be executed concurrently.
#It waits for all the tasks to complete before proceeding.
# This is useful when calling APIs because it enables the program to make multiple API requests at the same time, rather than waiting for each request to finish before starting the next one.
#This can significantly reduce the total time taken to complete all API calls, especially when dealing with I/O-bound operations like network requests.

"""
43Q)
Write an asynchronous program that makes three API calls concurrently using httpx.AsyncClient and asyncio.gather().

You don't need a real API URL; use:

https://example.com"""
import asyncio
import httpx

async def fetch(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)
    return {
        "url": str(response.url),
        "status": response.status_code,
        "text_length": len(response.text),
    }

async def main():
    urls = [
        "https://example.com",
        "https://example.com",
        "https://example.com",
    ]

    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

if __name__ == "__main__":
    data = asyncio.run(main())
    print(data)

"""Rboto3 / AWS S3"""
import boto3
"""44Q)
Write code to create an S3 client.

Then explain what this represents:

boto3.client("s3")"""

s3 = boto3.client("s3")
#client("s3") creates a low-level client representing Amazon Simple Storage Service (S3).
#  This client allows you to interact with S3, enabling you to perform operations such as listing buckets, uploading and downloading files, and managing objects within S3 buckets.
#  It serves as the interface through which your Python code communicates with the S3 service.


"""44Q)
Write code to:

list buckets
list objects inside a bucket
upload a local file
download an S3 object.

Name the relevant methods."""
s3.list_buckets()
s3.list_objects_v2(Bucket='your-bucket-name')
s3.upload_file('local-file.txt', 'your-bucket-name', 's3-key.txt')
s3.download_file('your-bucket-name', 's3-key.txt', 'downloaded-file.txt')


"""45Q)
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

Why is S3 commonly used as a data lake/storage layer?"""
#s3 is commonly used as a data lake/storage layer because it provides scalable, durable, and cost-effective storage for large amounts of structured and unstructured data.
#  It allows for easy integration with various data processing and analytics tools, supports multiple data formats, and enables efficient data retrieval and management. 
# Additionally, S3's features like versioning, access control, and lifecycle policies make it suitable for long-term data storage and compliance requirements.


"""46Q)
Your program says:

students.json uploaded successfully

but S3 shows:

students.json
Size: 0 bytes

List at least 4 possible causes."""
#1. The file was not properly closed before uploading.
#2. The file path is incorrect.
#3. The file is empty or corrupted.
#4. There was an error during the upload process.

"""47Q)
Write a short program that:

1. creates an S3 client
2. uploads students.json
3. lists objects under raw/
4. prints their keys

Use boto3."""
import boto3

s3 = boto3.client("s3")

# 1. Create an S3 client
# 2. Upload students.json
s3.upload_file("students.json", "your-bucket-name", "raw/students.json")

# 3. List objects under raw/
response = s3.list_objects_v2(Bucket="your-bucket-name", Prefix="raw/")

# 4. Print their keys
for obj in response.get("Contents", []):
    print(obj["Key"])

