'''
Does the solution calculate solstices/equinoxes using skyfield.almanac.seasons()?
Does the solution use find_discrete(...) to get season start times?
'''
import ast
import sys

FILE_PATH = "/root/repo/core/homeassistant/components/season/sensor.py"

try:
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        code = file.read()
        tree = ast.parse(code)

    uses_seasons_func = False
    uses_find_discrete = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "seasons":
                    uses_seasons_func = True
                if node.func.id == "find_discrete":
                    uses_find_discrete = True
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr == "seasons":
                    uses_seasons_func = True
                if node.func.attr == "find_discrete":
                    uses_find_discrete = True

    if uses_seasons_func and uses_find_discrete:
        print("PASS: 'seasons()' and 'find_discrete()' are used for seasonal calculations.")
        sys.exit(0)
    if not uses_seasons_func:
        print("FAIL: 'seasons()' is not used for seasonal calculations.")
    if not uses_find_discrete:
        print("FAIL: 'find_discrete()' is not used to get season start times.")
    sys.exit(1)

except FileNotFoundError:
    print(f"FAIL: File {FILE_PATH} not found."); sys.exit(1)
except SyntaxError as e:
    print(f"FAIL: Syntax error in file: {e}"); sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error occurred: {e}"); sys.exit(1)
