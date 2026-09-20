#ChainMap is a class that groups multiple dictionaries or mappings together to create a single, updateable view.
from collections import ChainMap
import os
import argparse

cm = ChainMap({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
print(cm['a'])  # Output: 1

static_file_settings = {'host': 'localhost', 'port': 8080, 'debug': False}

#Environment-specific variable settings
env_var_settings = {
    'host': os.environ.get('APP_HOST'),
    'port': int(os.environ.get('APP_PORT', 8080)),
    'debug': os.environ.get('APP_DEBUG', 'False').lower() == 'true'
}
# Remove any environment variables that are missing
env_var_settings = {k: v for k, v in env_var_settings.items() if v is not None}

#Command-line argument settings
parser = argparse.ArgumentParser(description='Application settings')
parser.add_argument('--host', help='Host address')
parser.add_argument('--port', type=int, help='Port number')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
cmd_args = vars(parser.parse_args())
# Remove any command-line arguments that are missing
cmd_line_args = {k: v for k, v in cmd_args.items() if v is not None}

# Combine dictionaries using ChainMap
combined_settings = ChainMap(cmd_line_args, env_var_settings, static_file_settings)

# Accessing command-line application settings
print("settings:")
print(f"Host: {combined_settings['host']}")
print(f"Port: {combined_settings['port']}")
print(f"Debug_Mode: {combined_settings['debug']}")

#named tuples are immutable sequences, typically used to store collections of heterogeneous data. 
# They can be used as keys in dictionaries and as elements of sets, while lists cannot.
#  Tuples are defined by enclosing the elements in parentheses ().
from collections import namedtuple

Book = namedtuple('Book', ['title', 'author', 'year'])
bnw = Book(title='Brave New World', author='Aldous Huxley', year=1932)

print(f"Title: {bnw.title}, Author: {bnw.author}, Year: {bnw.year}")
print(f"{bnw[0]} was written by {bnw[1]} in {bnw[2]}.")

print(f"Named tuple as dictionary: {bnw._asdict()}")

"""deque is a double-ended queue with fast appends and pops on either end."""
from collections import deque

def palindrome(word):
    d = deque(word)
    while len(d) > 1:
        if d.popleft() != d.pop():
            return False
    return True
word = "radar"
if palindrome(word):
    print(f"{word} is a palindrome.")
else:
    print(f"{word} is not a palindrome.")