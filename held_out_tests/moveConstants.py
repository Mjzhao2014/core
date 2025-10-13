'''
Does the solution move the following from the sensor.py file to the const.py file?
- EQUATOR
- NORTHERN
- SOUTHERN
- STATE_AUTUMN
- STATE_SPRING
- STATE_SUMMER
- STATE_WINTER
- HEMISPHERE_SEASON_SWAP
Also checks that sensor.py imports const.py.
'''

import ast
import sys

SENSOR_PATH = "/root/repo/core/homeassistant/components/season/sensor.py"
CONST_PATH = "/root/repo/core/homeassistant/components/season/const.py"

CONSTANT_NAMES = {
    "EQUATOR",
    "NORTHERN",
    "SOUTHERN",
    "STATE_AUTUMN",
    "STATE_SPRING",
    "STATE_SUMMER",
    "STATE_WINTER",
    "HEMISPHERE_SEASON_SWAP",
}

def extract_constant_names(tree):
    constants = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in CONSTANT_NAMES:
                    constants.add(target.id)
        elif isinstance(node, ast.AnnAssign):  # <- Support for Final annotations
            if isinstance(node.target, ast.Name) and node.target.id in CONSTANT_NAMES:
                constants.add(node.target.id)
    return constants

def check_const_import(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "const" in node.module:
                return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if "const" in alias.name:
                    return True
    return False

try:
    with open(SENSOR_PATH, "r", encoding="utf-8") as f_sensor:
        sensor_code = f_sensor.read()
        sensor_tree = ast.parse(sensor_code)
        sensor_constants = extract_constant_names(sensor_tree)
        has_const_import = check_const_import(sensor_tree)

    with open(CONST_PATH, "r", encoding="utf-8") as f_const:
        const_code = f_const.read()
        const_tree = ast.parse(const_code)
        const_constants = extract_constant_names(const_tree)

    all_moved = not sensor_constants and CONSTANT_NAMES.issubset(const_constants)

    if all_moved and has_const_import:
        print("PASS: All constants moved to const.py, removed from sensor.py, and const.py is imported.")
        sys.exit(0)

    if sensor_constants:
        print(f"FAIL: The following constants are still in sensor.py: {sorted(sensor_constants)}")
    if not CONSTANT_NAMES.issubset(const_constants):
        missing = CONSTANT_NAMES - const_constants
        print(f"FAIL: The following constants are missing from const.py: {sorted(missing)}")
    if not has_const_import:
        print("FAIL: sensor.py does not import from const.py")
    sys.exit(1)

except FileNotFoundError as e:
    print(f"FAIL: File not found: {e.filename}"); sys.exit(1)
except SyntaxError as e:
    print(f"FAIL: Syntax error in file: {e}"); sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error occurred: {e}"); sys.exit(1)
