from functools import cache, cached_property, lru_cache, partial
import time

def fib(n):
   if n <=1:
       return n
   return fib(n-1) + fib(n-2)

@cache
def cached_fib(n):
    if n <= 1:
        return n
    return cached_fib(n-1) + cached_fib(n-2)

def bench_fib():
    goal = 38
    start = time.time()
    fib(goal)
    print(f"Time taken without coaching: {time.time() - start:.5f} seconds")

    start = time.time()
    fib(goal)
    print(f"Time taken with caching: {time.time() - start:.5f} seconds")



@lru_cache(maxsize = None)
def add_5(num):
    print(f"Adding 5 to {num}")
    return num + 5
bench_fib()
cached_fib(3)
add_one = partial(add_5(5), 1)
print(add_one(4))
print(fib.cache_info())
#Time taken without coaching: 27.42129 seconds
#Time taken with caching: 18.61043 seconds
