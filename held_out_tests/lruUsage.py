"""
Does the solution use Skyfield's LRU caching decorator, @lru_cache, to cache any expensive calculation, like loading the ephemeris file?
Also checks that it is properly imported from functools.
"""

import ast
import sys

FILE_PATH = "/root/repo/core/homeassistant/components/season/sensor.py"

def find_lru_cache_usage(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                # Handles: @lru_cache
                if isinstance(decorator, ast.Name) and decorator.id == "lru_cache":
                    return True
                # Handles: @something.lru_cache
                elif isinstance(decorator, ast.Attribute) and decorator.attr == "lru_cache":
                    return True
                # Handles: @lru_cache(...) or @functools.lru_cache(...)
                elif isinstance(decorator, ast.Call):
                    func = decorator.func
                    if isinstance(func, ast.Name) and func.id == "lru_cache":
                        return True
                    elif isinstance(func, ast.Attribute) and func.attr == "lru_cache":
                        return True
    return False

def check_lru_cache_import(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "functools":
                for alias in node.names:
                    if alias.name == "lru_cache":
                        return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "functools":
                    return True
    return False

try:
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        code = file.read()
        tree = ast.parse(code)

    used = find_lru_cache_usage(tree)
    imported = check_lru_cache_import(tree)

    if used and imported:
        print("PASS: '@lru_cache' is used and properly imported from functools.")
        sys.exit(0)
    if not used:
        print("FAIL: '@lru_cache' is not used to cache any expensive calculations.")
    if not imported:
        print("FAIL: 'lru_cache' is not imported from functools.")
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
