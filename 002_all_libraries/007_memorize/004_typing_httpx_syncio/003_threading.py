"""
threading + multiprocessing + multithreading"""
import threading
import time
"""
Q60 Write a program that creates two threads.

Each thread should print:

Task started:thread1.create()
Task finished:thread1.join()

Explain why threading is useful for I/O-bound Data Engineering workloads.
I/o bound workloads are tasks that spend a significant amount of time waiting for input/output operations to complete, 
such as reading from or writing to a database, making network requests, or accessing files.
 Threading is useful for I/O-bound workloads because it allows multiple threads to run concurrently,
 enabling the program to continue executing other tasks while waiting for I/O operations to finish. 
 This can lead to improved performance and responsiveness in applications that involve a lot of I/O operations.
"""
import multiprocessing
"""
Q61 — multiprocessing

Explain the fundamental difference between:

thread:A thread is a lightweight unit of execution within a process that shares the same memory space as other threads in the same process. Threads are useful for I/O-bound tasks because they can run concurrently, allowing the program to perform other operations while waiting for I/O to complete. However, due to Python's Global Interpreter Lock (GIL), only one thread can execute Python code at a time, which can limit performance for CPU-bound tasks.
process:A process is an independent unit of execution that has its own memory space and resources. Processes are useful for CPU-bound tasks because they can run in parallel on multiple CPU cores, allowing for true parallelism. Each process can execute Python code independently, bypassing the limitations of the GIL and improving performance for tasks that require significant computation.

Then explain why multiprocessing can help CPU-bound Python work.
processing can help CPU-bound Python work because it allows for true parallelism by creating separate processes, each with its own Python interpreter and memory space. This means that multiple processes can run simultaneously on different CPU cores, enabling the program to fully utilize the available processing power. Since CPU-bound tasks involve heavy computation, multiprocessing can significantly improve performance by distributing the workload across multiple processes, bypassing the limitations of the Global Interpreter Lock (GIL) that restricts concurrent execution of Python code in threads.
"""

"""
Q62 — choose the correct tool

For each situation, choose:

normal synchronous: When the task is simple and doesn't require a lot of resources or time.
threading: When the task is I/O-bound and can benefit from concurrent execution.
asyncio: When the task is I/O-bound and you want to use asynchronous programming for better performance.
multiprocessing: When the task is CPU-bound and you need true parallelism to utilize multiple CPU cores.

and explain why.

A. Download 10,000 files from S3.: threading

B. Make 1,000 API requests.: asyncio

C. Perform CPU-heavy transformation on 20 GB of data.: multiprocessing

D. Run three simple sequential database queries where each depends on the previous result.: normal synchronous

D. Run three simple sequential database queries where each depends on the previous result. : normal synchronous"""

"""
Q63

You receive:

students.json

containing 100,000 student records.

Design the Python/Data Engineering pipeline:

INPUT
  ↓
read JSON
  ↓
transform/clean records
  ↓
validate/clean data
  ↓
DATABASE

Your solution must use concepts from at least 8 of the topics you've been tested on.

Explain:

how you discover the file : for example, you could use the os module to check for the existence of the file in a specific directory or use glob to search for files matching a certain pattern.
how you read JSON: You can use the built-in json module to read the JSON file. Open the file using a context manager (with statement) and use json.load() to parse the JSON data into a Python dictionary or list.
how you validate/clean records: You can use functions to validate each record's fields, checking for required fields, data types, and value ranges. For cleaning, you can remove or correct invalid records, normalize data formats (e.g., date formats), and handle missing values by filling them with defaults or removing the records.
how you handle logging: You can use the logging module to log important events, errors, and warnings during the pipeline execution. Set up a logger with appropriate log levels (DEBUG, INFO, WARNING, ERROR) and configure it to write logs to a file or console for monitoring and debugging purposes.
how you handle dates:dates can be handled using the datetime module. You can parse date strings into datetime objects, perform date arithmetic, and format dates as needed. For validation, you can check if the dates fall within acceptable ranges or if they are in the correct format.
how you deal with errors: You can use try-except blocks to catch and handle exceptions that may occur during the pipeline execution. You can log errors and warnings to help with debugging and monitoring.
how you load into a database: You can use a database connector library (e.g., psycopg2 for PostgreSQL, pymysql for MySQL) to connect to the database. Use parameterized queries or an ORM (Object-Relational Mapping) tool to insert the cleaned and validated records into the appropriate database tables. Ensure proper transaction management and error handling during the database operations.
where concurrency could be useful: Concurrency can be useful in scenarios where you have I/O-bound operations, such as reading from a file or making API requests. By using threading or asyncio, you can perform these operations in parallel, improving the overall performance of the pipeline.
where AWS S3 could fit: AWS S3 can be used to store the JSON file and any intermediate or final results. This allows for easy access and retrieval of data, as well as backup and archival purposes.
which parts should not be made concurrent and why: Parts of the pipeline that involve CPU-bound operations or operations that are inherently sequential should not be made concurrent. For example, data validation and transformation logic that depends on the order of operations should be executed sequentially to ensure data integrity and correctness.

Then write a short pseudocode/program skeleton for the pipeline.
class DataPipeline:
    def __init__(self, input_file, db_connection):
        self.input_file = input_file
        self.db_connection = db_connection
        self.logger = self.setup_logger()
        read self.data = []
    def setup_logger(self):
    return logger
    def discover_file(self):
        # Use os or glob to check for the existence of the file
        file_path = os.path.join("path/to/directory", self.input_file)
        if os.path.exists(file_path):
            return file_path
        else:
            raise FileNotFoundError("File not found")
"""