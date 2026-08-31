from functools import singledispatch, warps, reduce, partial, lru_cache, total_ordering
def mylogger(func):

    def wrapper(*args, **kwargs):
        print(f"Running {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
@mylogger
def add(a,b):
    """add a and b """
    return a + b
print(1,2) # add 1 and 2 result is 3
print(add.__name__) # wrapper
print(add.__doc__)

def append_one(obj):
    if type(obj) == list:
        return obj + [1]
    elif type(obj) == set:
        return obj.union({1})
    elif type(obj) == str:
        return obj + str(1)
    else:
        print("Unsupported type")
        return obj
print(append_one([1,2,3]))
print(append_one({1,2,3}))
print(append_one("abcde"))
"""Single dispatch"""
@singledispatch
def append_one(obj):
    print("Unsupported type")
    return obj

@append_one.register(list)
def _(obj):
   return obj + [1]

@append_one.register(set)
def _(obj):
   return obj.union({1})

@append_one.register(str)
def _(obj):
   return obj + str(1)

print(append_one([1,2,3]))
print(append_one({1,2,3}))