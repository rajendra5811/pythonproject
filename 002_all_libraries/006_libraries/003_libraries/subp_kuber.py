import subprocess

#kubernetes command to get the list of pods in the default namespace
result = subprocess.run(["kubectl", "get", "pods", "-n", "default"], capture_output=True, text=True)
if result.returncode == 0:
    with open("pods_list.txt", "w") as file:
        file.write(result.stdout)
    print(f"Output:\n{result.stdout}")
else:
    print(f"Error:\n{result.stderr}")

print(result.stdout)
print(result.stderr)
print(f"Return code: {result.returncode}")