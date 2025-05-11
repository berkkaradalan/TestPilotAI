import re
import json
import subprocess

def read_json_file(file_path:str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"🚨 Error reading JSON file: {e}")
        return None    

def validate_open_api(openapi_data: dict) -> bool:
    try:
        return bool(openapi_data.get("openapi"))
    except KeyError:
        return False
    except AttributeError:
        return False
    except TypeError:
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
def get_tree_output(path, ignore_dirs=None):
    ignore_dirs = ignore_dirs or []
    cmd = ["tree", "-I", "|".join(ignore_dirs), path]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return output.decode("utf-8")
    except FileNotFoundError:
        return "Error --> 'tree' command is not installed. Please install it using: sudo apt install tree"
    except subprocess.CalledProcessError as e:
        return f"Error --> An error occurred while executing the tree command: {e}"
    


def get_endpoint_names_from_scenario_result(test_scenario: str) -> str:
    if not test_scenario or not isinstance(test_scenario, str):
        raise TypeError("test_scenario must be a non-empty string")
    matches = re.findall(r'^testcase_(.*?):', test_scenario, re.MULTILINE)
    return "\n".join(matches)