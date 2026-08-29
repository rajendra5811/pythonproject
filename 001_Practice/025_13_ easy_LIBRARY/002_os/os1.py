import os
print(os.getcwd()) # current directory
print('//')
print(os.listdir())#list of directories
#how do you charge your cwd
#os.chdir(r"C:\Users\Desktop\Sample")
print(os.getcwd())
#list directories and files
print(os.listdir())
os.mkdir('good')
print(os.getcwd())
for root, directory, file in os.walk(os.getcwd()):
    print(root)
    print(directory)

