'''
Does the solution import Skyfield in sensor.py and delete the ephem import?
'''

import ast
import sys

FILE_PATH = "/root/repo/core/homeassistant/components/season/sensor.py"

try:
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        code = file.read()
        tree = ast.parse(code)

    has_ephem_import = False
    has_skyfield_import = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("ephem"):
                    has_ephem_import = True
                if alias.name.startswith("skyfield"):
                    has_skyfield_import = True

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if node.module.startswith("ephem"):
                    has_ephem_import = True
                if node.module.startswith("skyfield"):
                    has_skyfield_import = True

    if has_ephem_import:
        print("FAIL: 'ephem' is still imported in sensor.py.")
        sys.exit(1)
    if not has_skyfield_import:
        print("FAIL: No 'skyfield' imports found in sensor.py.")
        sys.exit(1)

    print("PASS: 'skyfield' is imported and 'ephem' is removed in sensor.py.")
    sys.exit(0)

except FileNotFoundError:
    print(f"FAIL: File {FILE_PATH} not found.")
    sys.exit(1)
except SyntaxError as e:
    print(f"FAIL: Syntax error in file: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error occurred: {e}")
    sys.exit(1)

