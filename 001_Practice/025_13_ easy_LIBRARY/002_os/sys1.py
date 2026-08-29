import sys
name = input()
if len(sys.argv) < 2:
    print("Please provide your name", name)
    #sys.exit("Access Denied")
else:
    name = str(sys.argv[1])
    print("Hello",name)
#name = str(sys.argv[1])
print("Hello", name)
print(sys.argv[0])
print(sys.version)
print(sys.version_info)
print(sys.platform)
sys.stdout.write("Hello\n")
