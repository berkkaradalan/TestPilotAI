import re
import sys
import subprocess
from importlib.util import find_spec
from pathlib import Path
from typing import Set

def detect_required_packages(test_code: str) -> Set[str]:
    """Test kodunu analiz ederek gerekli paketleri belirler"""
    base_requirements = {'pytest'}  # Her zaman gerekli temel paket
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
    """Eksik paketleri yükler ve başarı durumunu döndürür"""
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
    required_packages = detect_required_packages(test_code)
    if not install_packages(required_packages):
        return False
    
    test_dir = Path(project_path) / "generated_tests"
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "generated_test.py"
    try:
        test_file.write_text(test_code, encoding="utf-8")
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        print("\n" + "📜 TEST RESULTS ".ljust(80, "="))
        print(result.stdout)
        print("="*80 + "\n")
        
        return result.returncode == 0
    except Exception as e:
        print(f"🔥 Unexpected error: {str(e)}")
        return False
    finally:
        try:
            test_file.unlink()
        except Exception as e:
            print(f"⚠️ Error cleaning up test file: {str(e)}")