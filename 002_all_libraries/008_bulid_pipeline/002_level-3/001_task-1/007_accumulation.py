import itertools
import operator

# Example of using itertools.accumulate
numbers = [1, 2, 3, 4, 5]
b = ['a', 'b', 'c', 'd', 'e']
accumulated = list(itertools.accumulate(numbers, operator.mul))
print(accumulated)  # Output: [1, 2, 6, 24, 120]
combined = list(itertools.accumulate(zip(numbers, b)))
print(combined)  

l = [1, 2, 3, 4, 5]
selectors = [True, False, True, False, True]
compressed = itertools.compress(l, selectors)
print(list(compressed))  # Output: [1, 3, 5]

remaining = itertools.dropwhile(lambda x: x < 3, l)
print(list(remaining))  # Output: [3, 4, 5]

filtered = itertools.filterfalse(lambda x: x % 2 == 0, l)
print(list(filtered))  # Output: [1, 3, 5]