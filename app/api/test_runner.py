import re
import sys
import subprocess
from importlib.util import find_spec
from pathlib import Path
from typing import Set, List
from .openrouter import send_request_to_openrouter
from .prompts import pytest_error_prompt
from app.api.file_functions import append_test_code_to_file


def install_requirements_txt(project_path: str) -> bool:
    req_file = Path(project_path) / "requirements.txt"
    if req_file.exists():
        print("📦 Installing requirements.txt packages...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=120
            )
            print("✅ requirements.txt packages installed")
            return True
        except subprocess.CalledProcessError as e:
            print("❌ Failed to install requirements.txt. Error output:\n{e.output}")
            return False
        except subprocess.TimeoutExpired:
            print("⏰ requirements.txt installation timed out")
            return False
    else:
        print("ℹ️ No requirements.txt file found at {project_path}")
        return True


def detect_required_packages(test_code: str) -> Set[str]:
    base_requirements = {'pytest'}
    patterns = [
        r'^\s*import\s+([^\s.]+)',
        r'^\s*from\s+([^\s.]+)',
        r'client\s*=\s*TestClient\(',
        r'@pytest\.fixture'
    ]
    
    detected = set()
    for line in test_code.split('\n'):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                if 'TestClient' in line:
                    detected.update(['fastapi', 'pytest'])
                elif 'pytest' in line:
                    detected.add('pytest')
                elif match.group(1):
                    lib = match.group(1).split('.')[0]
                    detected.add(lib)
    
    return base_requirements.union(detected)

def install_packages(packages: Set[str], timeout: int = 60) -> bool:
    if not packages:
        return True
        
    missing = [pkg for pkg in packages if not find_spec(pkg)]
    if not missing:
        return True

    print(f"🔍 Missing packages detected: {', '.join(missing)}")
    
    try:
        cmd = [
            sys.executable, "-m", "pip", "install",
            "--disable-pip-version-check",
            "--no-warn-script-location",
            *missing
        ]
        
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout
        )
        print(f"✅ Successfully installed packages")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages. Error output:\n{e.output}")
        return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Package installation timed out after {timeout} seconds")
        return False

def run_tests_safely(test_code: str, project_path: str) -> tuple[str, bool]:
    if not install_requirements_txt(project_path):
        return "", False
    required_packages = detect_required_packages(test_code)
    if not install_packages(required_packages):
        return "", False

    test_dir = Path(project_path)
    test_file = test_dir / "test_runner.py"
    try:
        test_file.write_text(test_code, encoding="utf-8")

        result = subprocess.run(
            ["python3", "test_runner.py"],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        output = result.stdout + "\n" + result.stderr
        return output, result.returncode == 0
    except Exception as e:
        return f"🔥 Unexpected error: {str(e)}", False
    finally:
        try:
            test_file.unlink()
        except Exception as e:
            print(f"⚠️ Error cleaning up test file: {str(e)}")

def attempt_test_fix_loop(
    api_key: str,
    model_name: str,
    test_code: str,
    test_scenario: str,
    tree_struct: str,
    project_path: str,
    max_attempts: int = 10,
    auth_token_endpoint_prompt: str = "",
    auth_register_endpoint_prompt: str = "",
):
    attempt = 0
    current_test_code = test_code

    while attempt < max_attempts:
        print(f"🚀 Attempt {attempt + 1}/{max_attempts}")
        
        test_run_output, execution_success = run_tests_safely(test_code=current_test_code, project_path=project_path)
        
        if execution_success and not any(keyword in test_run_output for keyword in ["FAILED", "ERROR", "assert", "AssertionError"]):
            print("✅ All tests passed successfully!")
            return current_test_code
        
        print(f"⚠️ Tests had issues in attempt {attempt + 1}:")
        error_lines = [line for line in test_run_output.splitlines() if any(kw in line for kw in ["FAILED", "ERROR", "assert", "AssertionError"])]
        for line in error_lines[:5]:
            print(f"  {line}")
        
        if attempt + 1 >= max_attempts:
            user_input = input("⚠️  Maximum attempts reached. Do you want to continue? (y/n): ").strip().lower()
            if user_input == "y":
                max_attempts += 1
            elif user_input == "n":
                print("🛑 Stopping the fixing process without saving failed test.")
                return None
            else:
                print("❓ Please enter 'y' or 'n'.")
                continue
        
        prompt = (
            pytest_error_prompt + "\n\n"
            + "- Current test code : " + "\n" + current_test_code + "\n\n"
            + "- Error output : " + "\n" + test_run_output + "\n\n"
            + "- Test Scenario : " + "\n" + test_scenario + "\n\n"
            + "- Tree Structure : " + "\n" + tree_struct + "\n"
            + "- Auth token endpoint : " + "\n" + auth_token_endpoint_prompt + "\n" + "- Auth register endpoint : " + "\n" + auth_register_endpoint_prompt + "\n"
        )

        fixed_code = send_request_to_openrouter(
            api_key=api_key,
            model_name=model_name,
            prompt=prompt
        )

        current_test_code = fixed_code
        attempt += 1
    
    return None
