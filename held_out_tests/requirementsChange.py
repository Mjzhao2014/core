'''
Does the solution change the requirement in requirements_test_all.txt and requirements_all.txt from ephem==4.1.6 to Skyfield?
'''

import sys

FILES = [
    "/root/repo/core/requirements_test_all.txt",
    "/root/repo/core/requirements_all.txt"
]

def check_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"FAIL: File {path} not found.")
        return False

    # More precise check
    has_ephem = any(line.strip().startswith("ephem==") for line in lines)
    has_skyfield = any("skyfield" in line.lower() for line in lines)

    if has_ephem:
        print(f"FAIL: 'ephem' is still present in {path}.")
    if not has_skyfield:
        print(f"FAIL: 'skyfield' is not found in {path}.")

    return not has_ephem and has_skyfield

all_passed = True
for file in FILES:
    if not check_file(file):
        all_passed = False

if all_passed:
    print("PASS: Both requirements files have migrated to skyfield and removed ephem.")
    sys.exit(0)
else:
    sys.exit(1)
