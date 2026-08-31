import re

email = "raj@gmail.com"

pattern = r"^[\w.-]+@[\w.-]+\.\w+$"

if re.match(pattern, email):
    print("Valid")
else:
    print("Invalid")

match = re.search(r"\.",email)
print(match)