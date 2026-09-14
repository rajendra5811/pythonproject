import subprocess

result = subprocess.run(["docker", "run", "-d", "-p", "8080:8080", "--name", "my_container"], capture_output=True, text=True, timeout=10)
print(result.stdout)
print(result.stderr)
print(f"Return code: {result.returncode}")
#open docker and run the container in detached mode, mapping port 8080 of the host to port 8080 of the container. The output of the command is captured and printed to the console.
# i don't know if this terraform command will work, but it is an example of how to run a terraform command using subprocess in python. 
# The command is run in the specified directory and the output is captured and printed to the console.
terrafrom_dir ="/home/user/terraform_project"

try:
    result = subprocess.run(["terraform", "init"], cwd=terrafrom_dir, capture_output=True, text=True, timeout=30)
    print(result.stdout)
    print(result.stderr)
    print(f"Return code: {result.returncode}")
except subprocess.TimeoutExpired:
    print("The command timed out.")
except Exception as e:
    print(f"An error occurred: {e}")