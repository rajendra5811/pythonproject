
"""regex"""
#30Q)Given:"X = student_101@example.com"
import re
#a)write a regular expression that extracts like student_101, example.com
print(re.match(r"/@A"))
print(re.match(r"/@B"))
#b)Which re function would you use to extract all occurrences of a pattern in a string?
#re.findall() would be used to extract all occurrences of a pattern in a string.
#re.search() would be used to find the first occurrence of a pattern in a string.
#re.match() would be used to check if the beginning of a string matches a pattern.
#re.sub() would be used to replace occurrences of a pattern in a string with a specified replacement.

"""31Q)Write a short program that takes:data = [" Raj ", "John123", " Alice ", "Bob456 "]
and uses re to remove digits from the names and .strip() to remove surrounding spaces.

Expected:

Raj
John
Alice
Bob"""
print(re.sub(r'\d+', '', " Raj ").strip()) #substitutes digits with an empty string and removes surrounding spaces
"""collections, logging, typing"""
import collections, logging, typing
"""32Q)What problem does each solve?
a)Counter: iterable counting, useful for counting occurrences of elements in a collection.
b)defaultdict: provides a default value for missing keys, useful for grouping or aggregating data without needing to check for key existence. 
c)deque: double-ended queue, useful for efficiently adding/removing elements from both ends of a collection.
d)namedtuple: lightweight, immutable data structure with named fields, useful for creating simple classes without boilerplate code.
"""
from collections import Counter
cities = ["Hyderabad", "Delhi", "Hyderabad", "Mumbai", "Delhi", "Delhi"]
#33Q)Write code using Counter to produce city frequencies.
city_frequencies = Counter(cities)
print(city_frequencies)

from collections import defaultdict

#34Q)Write code using defaultdict(list) to transform:
"""
[
    ("IT", "Raj"),
    ("HR", "John"),
    ("IT", "Alice"),
    ("HR", "Bob")
]

into:

{
    "IT": ["Raj", "Alice"],
    "HR": ["John", "Bob"]
}"""
default_dict = defaultdict(list)
data = [
    ("IT", "Raj"),
    ("HR", "John"),
    ("IT", "Alice"),
    ("HR", "Bob")
]   
for department, name in data:
    default_dict[department].append(name)

print(dict(default_dict))