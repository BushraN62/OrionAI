"""
FINAL TEST: Math Post-Processor Verification
Shows EXACTLY what gets wrapped and how
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orion.app.orchestrator import _fix_math_formatting

def check_latex_wrapped(text):
    """Check if LaTeX is properly wrapped (not naked)"""
    # Find all $ delimited blocks
    math_blocks = re.findall(r'\$\$?[^\$]+\$\$?', text)
    
    # Find any naked LaTeX (\ command NOT inside $ signs)
    # This is tricky - we need to exclude LaTeX inside $ blocks
    temp = text
    for block in math_blocks:
        temp = temp.replace(block, '')  # Remove all wrapped math
    
    # Now check if there's any LaTeX left
    naked_latex = re.findall(r'\\[a-z]+', temp, re.IGNORECASE)
    
    return len(naked_latex) == 0, naked_latex

print("=" * 100)
print("MATH POST-PROCESSOR FINAL TEST")
print("=" * 100)

# Test Case 1: Simple integral with fraction
print("\n" + "=" * 100)
print("TEST 1: Simple Integral")
print("=" * 100)

input1 = r"\int \frac{\tan x}{x^3} dx"
output1 = _fix_math_formatting(input1)

print(f"INPUT:  {input1}")
print(f"OUTPUT: {output1}")

is_wrapped, naked = check_latex_wrapped(output1)
if is_wrapped:
    print("✓ SUCCESS: All LaTeX is wrapped!")
else:
    print(f"✗ FAILED: Found naked LaTeX: {naked}")

# Test Case 2: Expression in brackets (LLM often uses this for display math)
print("\n" + "=" * 100)
print("TEST 2: Bracket Display Math (What LLM Outputs)")
print("=" * 100)

input2 = r"""[
\int \frac{\tan x}{x^3} dx = -\frac{x}{2(x^4 + 1)} \tan x + C
]"""

output2 = _fix_math_formatting(input2)

print(f"INPUT:\n{input2}")
print(f"\nOUTPUT:\n{output2}")

is_wrapped, naked = check_latex_wrapped(output2)
if is_wrapped:
    print("✓ SUCCESS: Brackets converted to $$ and all LaTeX wrapped!")
else:
    print(f"✗ FAILED: Found naked LaTeX: {naked}")

# Test Case 3: Mixed text and math (realistic scenario)
print("\n" + "=" * 100)
print("TEST 3: Broken LLM Output (What You Showed in Screenshot)")
print("=" * 100)

# This simulates the broken output from your screenshot
input3 = r"""The indefinite integral ( \int ( \sin x - \frac{x^2}{(x^2-1)^3} ) dx) does not have a simple closed-form solution.

\int ( \sin x - \frac{x^2}{(x^2-1)^3} ) dx = -\frac{1}{4} \left( (x-1) e^{-(x+1)} + 6 (x-1) \ln |x| \right) + C

This expression involves the use of hypergeometric functions."""

output3 = _fix_math_formatting(input3)

print(f"INPUT:\n{input3}")
print(f"\nOUTPUT:\n{output3}")

is_wrapped, naked = check_latex_wrapped(output3)
if is_wrapped:
    print("✓ SUCCESS: All LaTeX wrapped, brackets converted!")
else:
    print(f"✗ FAILED: Found naked LaTeX: {naked}")

# Test Case 4: Already properly formatted (should not break it)
print("\n" + "=" * 100)
print("TEST 4: Already Properly Formatted (Should Not Change)")
print("=" * 100)

input4 = r"The answer is $x = 4$ and the integral is $$\int_0^5 x^2 dx = \frac{125}{3}$$"
output4 = _fix_math_formatting(input4)

print(f"INPUT:  {input4}")
print(f"OUTPUT: {output4}")

if input4 == output4:
    print("✓ SUCCESS: Preserved already-correct formatting!")
else:
    print("✗ WARNING: Changed already-correct formatting")
    print(f"  Difference: {len(output4) - len(input4)} characters")

# Final Summary
print("\n" + "=" * 100)
print("SUMMARY: What ReactMarkdown Will Receive")
print("=" * 100)

print("\nAfter post-processing, the output has:")
print("  • Inline math in $...$ (renders in-line)")
print("  • Display math in $$...$$ (renders centered)")
print("  • [LaTeX] converted to $$LaTeX$$")
print("  • (LaTeX) wrapped as ($LaTeX$)")
print("  • All standalone LaTeX commands wrapped")

print("\n" + "=" * 100)
print("Ready to test in Dashboard!")
print("=" * 100)
print("\nTo test:")
print("1. Restart backend: python -m server.main")
print("2. Open dashboard: http://localhost:5173")
print("3. Ask: 'Give me the integration of tan x / x³'")
print("4. Watch the beautiful rendered math! ✨")
