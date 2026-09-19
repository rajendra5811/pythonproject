from functools import partial, cache, wraps, cached_property
import time

def with_greeting(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Hello! Executing the function...")
        return func(*args, **kwargs)
    return wrapper

@with_greeting
def add(a, b):
    """Adds two numbers and prints the result."""
    print(f"Adding {a} and {b} is {a + b}")
    return a + b

@cache
def subtract(a, b):
    """Subtracts two numbers and prints the result."""
    time.sleep(3)  
    print(f"Subtracting {b} from {a} is {a - b}")
    return a - b   

@cache
def multiply(a, b):
    time.sleep(2)  
    print(f"Multiplying {a} and {b} is {a * b}")
    return a * b 

if __name__ == "__main__":
    add(5, 7)  
    print(f"Function name: {add.__name__}")
    print(f"Function docstring: {add.__doc__}")
    partial_add = partial(add, 10) # partial(func, *args, **kwargs) 
    partial_add(15) 
    print(f"Function name: {subtract.__name__}")
    print(f"Function docstring: {subtract.__doc__}")
    print("CACHED:", subtract(8, 5))
    print("Not CACHED:", subtract(a=10, b=5))
    print("CACHED:", multiply(8, 5))
    print("Not CACHED:", multiply(8, 5)) 