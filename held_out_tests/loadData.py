'''
Does the solution load the planetary ephemeris with "load('de430.bsp')" using Skyfield?
'''
import ast
import sys

FILE_PATH = "/root/repo/core/homeassistant/components/season/sensor.py"

try:
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        code = file.read()
        tree = ast.parse(code)

    loads_de430 = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "load":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and arg.value == "de430.bsp":
                        loads_de430 = True
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "load":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and arg.value == "de430.bsp":
                        loads_de430 = True

    if loads_de430:
        print("PASS: 'load(\'de430.bsp\')' is used to load the planetary ephemeris with Skyfield.")
        sys.exit(0)
    else:
        print("FAIL: 'load(\'de430.bsp\')' is NOT found in the file.")
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
