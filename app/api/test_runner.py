import re
import sys
import subprocess
from importlib.util import find_spec
from pathlib import Path
from typing import Set
from .openrouter import send_request_to_openrouter
from .prompts import pytest_error_prompt

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

def run_tests_safely(test_code: str, project_path: str) -> bool:
    if not install_requirements_txt(project_path):
        return False
    required_packages = detect_required_packages(test_code)
    if not install_packages(required_packages):
        return False
    
    test_dir = Path(project_path)
    # test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "generated_test.py"
    try:
        test_file.write_text(test_code, encoding="utf-8")
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # print("\n" + "📜 TEST RESULTS ".ljust(80, "="))
        # print(result.stdout)
        # print("="*80 + "\n")
        
        return result.stdout
    except Exception as e:
        print(f"🔥 Unexpected error: {str(e)}")
        return False
    finally:
        try:
            test_file.unlink()
        except Exception as e:
            print(f"⚠️ Error cleaning up test file: {str(e)}")
            return False


def attempt_test_fix_loop(
    api_key: str,
    model_name: str,
    test_code: str,
    test_scenario: str,
    tree_struct: str,
    project_path: str,
    max_attempts: int = 10,
):
    attempt = 0
    current_test_code = test_code

    while True:
        print(f"🚀 Attempt {attempt + 1}/{max_attempts}")
        test_run_output = run_tests_safely(test_code=current_test_code, project_path=project_path)

        if test_run_output and "1 passed" in test_run_output.lower():
            print("✅ Test passed successfully!")
            return current_test_code

        if attempt + 1 >= max_attempts:
            user_input = input("⚠️  Maximum attempts reached. Do you want to continue? (y/n): ").strip().lower()
            if user_input == "y":
                max_attempts += 10
            elif user_input == "n":
                print("🛑 Stopping the fixing process.")
                return current_test_code
            else:
                print("❓ Please enter 'y' or 'n'.")
                continue
        else:
            prompt = (
                pytest_error_prompt + "\n\n"
                + "- Current test code : " + "\n" + current_test_code + "\n\n"
                + "- Error output : " + "\n" + test_run_output + "\n\n"
                + "- Test Scenario : " +  "\n" + test_scenario + "\n\n"
                + "- Tree Structure : " + "\n" + tree_struct
            )

            fixed_code = send_request_to_openrouter(
                api_key=api_key,
                model_name=model_name,
                prompt=prompt
            )


            current_test_code = fixed_code
            attempt += 1

