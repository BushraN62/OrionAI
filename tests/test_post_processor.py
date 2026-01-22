"""Test the post-processor directly"""
import sys
sys.path.insert(0, 'w:\\VS Code Projects\\Orion  ( Qwen2.5 VL 7B )')

from orion.app.orchestrator import _fix_math_formatting

# Test the exact input from the screenshot
test_input = r"""(u_1 v_1)^2 + (u_2 v_2)^2 + \cdots + (u_n v_n)^2."""

print("INPUT:")
print(repr(test_input))
print()

try:
    result = _fix_math_formatting(test_input)
    print("OUTPUT:")
    print(repr(result))
    print()
    print("RENDERED:")
    print(result)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
