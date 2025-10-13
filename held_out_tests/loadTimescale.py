'''
Does the solution load Skyfield's timescale with "load.timescale()"?
'''
import ast
import sys

FILE_PATH = "/root/repo/core/homeassistant/components/season/sensor.py"

try:
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        code = file.read()
        tree = ast.parse(code)

    uses_timescale = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "timescale" and isinstance(node.func.value, ast.Name):
                    if node.func.value.id == "load":
                        uses_timescale = True

    if uses_timescale:
        print("PASS: 'load.timescale()' is used to load Skyfield's timescale.")
        sys.exit(0)
    else:
        print("FAIL: 'load.timescale()' is not found in the file.")
        sys.exit(1)

except FileNotFoundError:
    print(f"FAIL: File {FILE_PATH} not found.")
    sys.exit(1)
except SyntaxError as e:
    print(f"FAIL: Syntax error in file: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error occurred: {e}")
    sys.exit(1)
