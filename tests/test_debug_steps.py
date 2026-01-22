"""Debug each step of the post-processor"""
import re

text = r"""\int \frac{\tan x}{x^3} dx"""

print("ORIGINAL:")
print(repr(text))
print()

# Step: Count commands
latex_commands = re.findall(r'\\[a-zA-Z]+', text)
print(f"Found {len(latex_commands)} LaTeX commands: {latex_commands}")
print()

# Step: Check if >= 3
if len(latex_commands) >= 3:
    stripped = text.strip()
    result = f'$$\n{stripped}\n$$'
    print("WRAPPED AS DISPLAY MATH:")
    print(repr(result))
    print()
    print("RENDERED:")
    print(result)
