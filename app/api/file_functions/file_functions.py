import json
import subprocess
import os
from config.rich_console import rich_console

class FileFunctions:
    def __init__(self):
        pass
    def append_test_code_to_file(test_code: str, project_path: str, filename: str = "test_runner.py"):
        file_path = os.path.join(project_path, filename)
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n\n")
            f.write(test_code)
        
        rich_console.success_string(f"Test code appended to {file_path}")

    def comment_out_code(code: str) -> str:
        return "\n# 🫸 FAILED TEST CODE (couldn't be fixed automatically) 🫷\n\n"+"\n".join(f"# {line}" for line in code.splitlines())

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