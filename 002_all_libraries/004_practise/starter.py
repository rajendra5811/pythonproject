import subprocess
from argparse import ArgumentParser
from pathlib import Path

subprocess.run(["firefox"])
subprocess.run(["notepad"])
subprocess.run(["texteditor"])
p1 = subprocess.run(["task",'add'], check=True)
print(p1.returncode)
# errorno2 : no such file or directory: 'task'

def project_starter(project_name):
    """ Creates a new project directory with project_name and then initialize with:
     1. Create a virtual environment
     2. Create a requirements.txt file"""
    project_dir = Path.cwd().absolute()/project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    print(project_dir)
    print(f"Starting a new project: {project_name}")

    # Create a requirements.txt file
    (project_dir/"requirements.txt").touch()

    # Create a virtual environment 
    subprocess.run(["python", "-m", "venv", str(project_dir/"venv")])

if __name__ == "__main__":

    parser = ArgumentParser(description="Start a new project")
    parser.add_argument("project_name", '-p', type = str, help = "Name of the project to be created")
    args = parser.parse_args()
    project_starter(args.project_name)