"""Test the ACTUAL post-processor function"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orion.app.orchestrator import _fix_math_formatting

test = r"\int \frac{\tan x}{x^3} dx"
result = _fix_math_formatting(test)

print("INPUT:")
print(repr(test))
print()
print("OUTPUT:")
print(repr(result))
print()
print("VISUAL:")
print(result)
