import json
import os

def load_json_file(file_path):
    blank_json = {}
    if os.path.exists(file_path):
        try:
            f = open(file_path, 'r')
            data = json.load(f)
            f.close()
            return data
        except ValueError as e:
            print("Decode error")
            return blank_json
    else:
        return blank_json

def saveJsonData(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON data: {e}")
        