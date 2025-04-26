import os
def append_test_code_to_file(test_code: str, project_path: str, filename: str = "test_runner.py"):
    file_path = os.path.join(project_path, filename)
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write(test_code)
    
    print(f"✅ Test code appended to {file_path}")