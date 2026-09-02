import subprocess

result = subprocess.run((['az', ' group', 'create', '--name', "new-rg2",'--location','centralindia']),
 caputre_output = True, text = True, check = True, timeout = 30) #Azure

print(f"Std output: {result.stdout}")
print(f"Return Code:{result.returncode}")
print(f"Error:{result.stderr}")