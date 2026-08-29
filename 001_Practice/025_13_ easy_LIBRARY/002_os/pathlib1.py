import os
from pathlib import Path, pathlib

path = os.getcwd()
print("Current directory:", path)

if not os.path.exists("data"):
    os.mkdir("data")
    print("data folder created")
else:
    print("data folder already exists")
os.path.join('dir1','dir2', 'file.txt')
os.exists()
print(pathlib.Path.cwd())
print(Path.cwd())
Path.home().joinpath('python','scripts','test.py')
path = Path.cmd()
