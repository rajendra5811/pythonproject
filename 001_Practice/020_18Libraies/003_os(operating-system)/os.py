import os

# 1. Find current working directory
current_dir = os.getcwd()
print("Current directory:", current_dir)

# 2. See what's inside it
print("Files/folders:", os.listdir())

# 3. Create data folder if it doesn't exist
if not os.path.exists("data"):
    os.mkdir("data")

# 4. Create nested folder structure
if not os.path.exists("data/raw/2026"):
    os.makedirs("data/raw/2026")

# 5. Build a file path safely
student_file = os.path.join(
    "data",
    "raw",
    "2026",
    "students.csv"
)

print("Student file path:", student_file)

# 6. Check whether the file exists
if os.path.exists(student_file):
    print("students.csv exists")
else:
    print("students.csv does not exist")

# 7. Read environment variable
database_url = os.getenv("DATABASE_URL")

print("DATABASE_URL:", database_url)