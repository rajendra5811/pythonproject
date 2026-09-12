#call() check_output() check_call() run()
"""subprocess.run(["command", "arg1", "arg2"], stdin = None, input=None,
 stdout=None, stderr=None, capture_output=False, shell = False, cwd=None, timeout=None, 
 check = False, text=True, check=True)"""
import subprocess
result = subprocess.run((), capture_output = True, text = True, check = True, timeout =30)
print(result.stderr)
print(result.stdout)
print(result.returncode)
result1 = subprocess.run((ps, "arg1", "arg2"), capture_output = True, text = True, check = True)
print(result1.stderr)
print(result1.stdout)
print(result1.returncode)

result2 = subprocess.run(["az","group","list"], capture_output = True, text = True, check = True)
print(result2.stderr)   
print(result2.stdout)
print(result2)