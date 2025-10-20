'''
Does the solution convert current date to a Skyfield datetime object using ts.utc(...) 
'''
import ast
import sys

FILE_PATH = "/root/repo/core/homeassistant/components/season/sensor.py"

try:
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        code = file.read()
        tree = ast.parse(code)

    uses_any_utc_call = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "utc":
                uses_any_utc_call = True

    if uses_any_utc_call:
        print("PASS: A Skyfield timescale object is used to call .utc(...)."); sys.exit(0)
    else:
        print("FAIL: No call to .utc(...) found on a timescale object."); sys.exit(1)

except FileNotFoundError:
    print(f"FAIL: File {FILE_PATH} not found."); sys.exit(1)
except SyntaxError as e:
    print(f"FAIL: Syntax error in file: {e}"); sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error occurred: {e}"); sys.exit(1)
