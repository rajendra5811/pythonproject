from pathlib import Path

path = Path.cwd()
print(path)

processed = Path("raw_data/processed")
processed.mkdir(parents=True, exist_ok=True)

print(processed.exists())
path.exists()
path.is_file()
path.is_dir()
path.name
path.suffix
path.parent
path.mkdir()
path.rmdir()
path.resolve()
path.with_name()
path.with_suffix()
path.glob()
import os
os.getcwd()
os.listdir()
os.path.join()
os.path.abspath()
os.path.isfile()
os.path.isdir()
import glob
glob.glob("*.py")
import math
math.ceil()
math.floor()
math.sqrt()
math.factorial()
import json
with open("data.json", "r") as f:
    data = json.load(f)
input_file = data/students.json
output_file = data/processed/students.json

json.dump(input_file)
json.load(output_file)
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]
sys.argv[0] → program.py
sys.argv[1] → input.json
sys.argv[2] → output.json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting the program")
logger.error("An error occurred")
logger.warning("This is a warning")
logger.debug("Debugging information")
logger.critical("Critical error")
logger.exception("Exception occurred", exc_info=True)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())