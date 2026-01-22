"""
Debug script to test math formatting post-processor
"""
import re
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the function from orchestrator
from orion.app.orchestrator import _fix_math_formatting

# Sample raw output from the LLM (like what we see in the screenshot)
test_cases = [
    # Case 1: Simple fraction in integral
    r"\int \frac{\tan x}{x^3} dx",
    
    # Case 2: Complex expression with multiple commands
    r"\int \frac{\tan x}{x^3} dx = -\frac{x}{2(x^4 + 1)} \tan x + \frac{1}{8(x^4 + 1)^2} \left(6x^5 \sec^2 x + 5x^3 \tan x (x^4 + 3) - 4x \ln |x| + 12(x^4 + 3)\right) + C",
    
    # Case 3: The actual output we see
    r"""The indefinite integral ( ∫ \frac{\tan x}{x^3} dx ) does not have a simple closed-form solution in terms of elementary functions such as polynomials, rational expressions, logarithms, exponential functions, or trigonometric and their inverses.

However, it can be expressed using special functions like the hypergeometric function. The integral is related to the hypergeometric function ( F(a, b, c; z) ):

[
\int \frac{\tan x}{x^3} dx = -\frac{x}{2(x^4 + 1)} \tan x + \frac{1}{8(x^4 + 1)^2} \left(6x^5 \sec^2 x + 5x^3 \tan x (x^4 + 3) - 4x \ln |x| + 12(x^4 + 3)\right) + C
]

This expression involves the use of hypergeometric functions, which are a class of special functions that generalize many other well-known special functions.""",
    
    # Case 4: Just the problem part
    r"-\frac{x}{2(x^4 + 1)} \tan x + \frac{1}{8(x^4 + 1)^2}",
]

print("=" * 80)
print("MATH FORMATTING POST-PROCESSOR DEBUG")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST CASE {i}:")
    print(f"{'='*80}")
    print("\n[INPUT] (Raw LaTeX from LLM):")
    print("-" * 80)
    print(test)
    print("-" * 80)
    
    # Process it
    result = _fix_math_formatting(test)
    
    print("\n[OUTPUT] (After post-processor):")
    print("-" * 80)
    print(result)
    print("-" * 80)
    
    # Check if it wrapped everything
    has_naked_latex = bool(re.search(r'(?<![\\$])\\[a-z]+', result))
    
    print("\n[STATUS]:")
    if has_naked_latex:
        print("FAILED - Still has naked LaTeX commands!")
        # Show what's still naked
        naked = re.findall(r'\\[a-z]+(?:\{[^}]*\})*', result)
        print(f"   Naked commands found: {naked[:5]}")  # Show first 5
    else:
        print("SUCCESS - All LaTeX is wrapped!")
    
    # Count $ signs
    dollar_count = result.count('$')
    print(f"   Dollar signs in output: {dollar_count}")
    if dollar_count % 2 != 0:
        print("   WARNING: Odd number of $ signs (unbalanced!)")

print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
