'''
Check whether sensor.py follows PEP 8 and PEP 257 style guidelines.
'''
import sys
import subprocess

FILE_PATH = "/root/repo/core/homeassistant/components/season/sensor.py"

try:
    # Run flake8 for PEP 8 compliance
    result_pep8 = subprocess.run(["flake8", "--max-line-length=88", FILE_PATH], capture_output=True, text=True)
    

    # Run pydocstyle for PEP 257 compliance
    result_pep257 = subprocess.run(["pydocstyle", FILE_PATH], capture_output=True, text=True)

    if result_pep8.returncode == 0 and result_pep257.returncode == 0:
        print("PASS: File follows PEP 8 and PEP 257 guidelines.")
        sys.exit(0)
    else:
        print("FAIL: File does not fully comply with PEP 8 and/or PEP 257.")
        if result_pep8.returncode != 0:
            print("PEP 8 Issues:\n", result_pep8.stdout)
        if result_pep257.returncode != 0:
            print("PEP 257 Issues:\n", result_pep257.stdout)
        sys.exit(1)

except FileNotFoundError:
    print(f"FAIL: File {FILE_PATH} not found.")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Error occurred: {e}")
    sys.exit(1)