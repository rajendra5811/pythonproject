#63-QUESTION DATA ENGINEERING MASTER DIAGNOSTIC
#PART A — Python Libraries: os, pathlib, sys, math

import os
import pathlib

#Q1)get the current working directory
print(os.getcwd())
#Q2)check whether data exists
print(os.path.exists("data"))
#Q3)create data/processed including missing parent directories.
os.makedirs("data/processed", exist_ok=True)
#pathlib
from pathlib import Path
#Q4)creates a Path
path = Path("data/students.json")
#Q5)checks whether the file exists
print(path.exists())
#Q6)prints the file name, suffix, and parent directory
print(path.name)
print(path.suffix)
print(path.parent)

#sys
import sys, json
#Q7)retrieve input.json and output.json from the command line
input_file = sys.argv[1]
output_file = sys.argv[2]
#Q8)Write code to: python program.py input.json output.json
#retrieve input.json and output.json from the command line.
input_file = data/students.json
output_file = data/processed/students.json
json.dump(input_file)
json.load(output_file)
#Q9)Which object/module gives you these arguments?
#The sys module gives you access to command line arguments through sys.argv.
###5 — math
import math
#Q10)Write code using math to:
#a)round a number upward
print(math.ceil(3.2))
#b)round a number downward
print(math.floor(3.8))
#c)calculate square root
print(math.sqrt(16))
#d)calculate factorial
print(math.factorial(5))

"""6 — os retrieval"""
#11Q)Without looking anything up, name 5 useful os functions/attributes that a Data Engineer might use.
os.getcwd() # Get the current working directory.
os.listdir() # List the contents of a directory.
os.path.join() # Join two or more path components.
os.path.abspath() # Return the absolute path of a file.
os.path.isfile() # Check if a path is a file.
os.path.isdir() # Check if a path is a directory.

""""7 — pathlib retrieval""""
#12Q)Name 6 useful Path methods/properties.
path.exists() # Check if a path exists.
path.is_file() # Check if a path is a file.
path.is_dir() # Check if a path is a directory.
path.name # Get the name of the file or directory.
path.suffix # Get the suffix of the file.
path.parent # Get the parent directory of the path.

#13Q)At least 2 must involve files/directories and 2 must involve path information.
path.mkdir() # Create a new directory.
path.rmdir() # Remove a directory.
path.resolve() # Get the absolute path of a file or directory.
path.with_name() # Change the name of a file or directory.
path.with_suffix() # Change the suffix of a file.
path.glob() # Find all files matching a pattern in a directory.
#Q14) — Write a program that:
#a)finds the current directory
 getcwd = Path.cwd()
 print(getcwd)
#b) creates a folder called raw_data
Path("raw_data").mkdir(exist_ok=True)
#c) creates a folder raw_data/processed
Path("raw_data/processed").mkdir(exist_ok=True)
#d) prints whether processed exists
print(Path("raw_data/processed").exists())