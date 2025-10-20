'''
Does the solution change the requirement in manifest.json from "ephem==4.1.6" to some Skyfield version?
Also checks that the logger name is changed from ephem to skyfield.
'''
import json
import sys

FILE_PATH = "/root/repo/core/homeassistant/components/season/manifest.json"

try:
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        code = file.read()
        manifest = json.loads(code)

    requirements = manifest.get("requirements", [])
    loggers = manifest.get("loggers", [])

    has_ephem_req = any("ephem" in req for req in requirements)
    has_skyfield_req = any("skyfield" in req for req in requirements)

    has_ephem_logger = any(logger == "ephem" for logger in loggers)
    has_skyfield_logger = any("skyfield" in logger for logger in loggers)

    passed = True

    if has_ephem_req:
        print("FAIL: 'ephem' is still present in requirements.")
        passed = False
    if not has_skyfield_req:
        print("FAIL: 'skyfield' is not found in requirements.")
        passed = False
    if has_ephem_logger:
        print("FAIL: 'ephem' is still listed in the loggers field.")
        passed = False
    if not has_skyfield_logger:
        print("FAIL: 'skyfield' is not listed in the loggers field.")
        passed = False

    if passed:
        print("PASS: manifest.json has migrated to skyfield correctly and updated logger field.")
        sys.exit(0)
    else:
        sys.exit(1)

except json.JSONDecodeError as e:
    print(f"FAIL: Failed to parse manifest.json: {e}")
    sys.exit(1)
except FileNotFoundError:
    print(f"FAIL: File {FILE_PATH} not found.")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error occurred: {e}")
    sys.exit(1)
