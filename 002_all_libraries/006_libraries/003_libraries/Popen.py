import subprocess
print(subprocess.__file__);
process = subprocess.Popen(["python"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
# kill (), terminate (), and wait () methods can be used to manage the process.
#  The communicate() method is used to send input to the process and read its output.
#  In this case, we are sending a simple Python command to print "Hello, World!" and capturing the output and error messages.
#  The return code of the process is also printed.
stdout, stderr = process.communicate(input = "print('Hello, World!')\n")
print(stdout)
print(stderr)
print(f"Return code: {process.returncode}")