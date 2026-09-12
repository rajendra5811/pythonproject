import subprocess
import sys

# 1. List directory (Unix-like systems)
# On Windows, use: ("dir",) with shell=True or Python's pathlib instead.
result1 = subprocess.run(
    ("ls", "-l"),
    capture_output=True,
    text=True,
    check=False  # don't fail script if ls is missing
)

# 2. Python version
result = subprocess.run(
    ["python", "--version"],
    capture_output=True,
    text=True,
    check=True
)

print("Python version output:")
print(result.stdout or result.stderr)

# 3. Install a package into the current environment
# Replace "package_name" with an actual package, e.g. "requests"
r = subprocess.run(
    [sys.executable, "-m", "pip", "install", "package_name"],
    check=True
)

print("pip install result:", r)
print("ls -l result:", result1)
print("ls -l stdout:\n", result1.stdout)
if result1.stderr:
    print("ls -l stderr:\n", result1.stderr)