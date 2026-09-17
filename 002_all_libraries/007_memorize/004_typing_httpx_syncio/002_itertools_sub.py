
"""PART I — itertools, functools, subprocess
Q51–Q54

Q51 — itertools

Explain and give one use case for:

chain():chain() is a function in the itertools module that takes multiple iterables as input and
        # returns a single iterable that produces items from the first iterable until it is exhausted, then continues to the next iterable, and so on.
        # This is useful for combining multiple sequences into one without creating intermediate lists.
product():product() is a function in the itertools module that computes the Cartesian product of input iterables.
         # It returns an iterator that yields tuples containing all possible combinations of elements from the input iterables. This is useful for generating all possible combinations of parameters or configurations in scenarios like testing or optimization.
combinations():combinations() is a function in the itertools module that returns all possible combinations of a specified length from the input iterable.
groupby():groupby() is a function in the itertools module that groups consecutive elements in an iterable that have the same key value.
islice():islice() is a function in the itertools module that allows you to create an iterator that returns selected elements from the input iterable, based on specified start, stop, and step parameters.
    It is useful for slicing iterables without creating intermediate lists.
"""
"""
Q52 — itertools coding

Given:

a = [1, 2]
b = [3, 4]

write code using itertools.chain() to produce:

1 2 3 4

Then use product() to produce all pairs."""

"""
Q53 — functools

Explain:

partial():partial() is a function in the functools module that allows you to fix a certain number of arguments of a function and generate a new function. This is useful for creating specialized versions of functions with some default parameters.
reduce():reduce() is a function in the functools module that applies a binary function cumulatively to the items of an iterable, reducing the iterable to a single value. It is useful for performing operations like summation, multiplication, or finding the maximum/minimum of a sequence.
lru_cache():lru_cache() is a decorator in the functools module that caches the results of a function call. It is useful for optimizing functions that are called repeatedly with the same arguments.
wraps():wraps() is a decorator in the functools module that helps preserve the metadata of the original function when creating a new function. It is useful for creating decorators that need to maintain the original function's name, docstring, and other attributes.

Give one Data Engineering-related use case for each. """
#partial(): A use case for partial() in Data Engineering could be creating a specialized function for data transformation that always applies a specific normalization technique to a dataset, allowing for consistent preprocessing across different datasets.
#reduce(): A use case for reduce() in Data Engineering could be aggregating a list of numerical values, such as calculating the total sales from a list of daily sales figures, by applying a summation function cumulatively.
#lru_cache(): A use case for lru_cache() in Data Engineering could be caching the results of a function that retrieves frequently accessed configuration settings from a database, reducing the number of database queries and improving performance.
#wraps(): A use case for wraps() in Data Engineering could be creating a decorator that logs the execution time of data processing functions while preserving the original function's metadata, allowing for better debugging and monitoring of data pipelines.

#Q54 — subprocess
import subprocess
"""Write Python code that executes:

python transform.py

from another Python program.

Then explain the difference between:

subprocess.run():subprocess.run() is a function in the subprocess module that runs a command in a new process, waits for it to complete, and returns a CompletedProcess instance containing information about the executed command, such as its return code and output. It is useful for executing external commands or scripts synchronously.
subprocess.Popen():
"""
#subprocess.Popen() is a class in the subprocess module that allows you to spawn a new process, connect to its input/output/error pipes, and obtain its return code. It provides more flexibility than subprocess.run() as it allows for asynchronous execution and interaction with the process while it is running. It is useful for scenarios where you need to manage long-running processes or communicate with them in real-time.