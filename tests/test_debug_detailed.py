"""Debug with print statements"""
import re

text = r"\int \frac{\tan x}{x^3} dx"

print("=" * 60)
print("STEP 1: Original text")
print(repr(text))
print()

# Simulate the protection (won't match anything here)
protected = {}
counter = [0]

# Step 2: Line processing
lines = text.split('\n')
print(f"STEP 2: Split into {len(lines)} lines")
processed_lines = []

for i, line in enumerate(lines):
    print(f"\n--- Processing line {i}: {repr(line)}")
    
    if not line.strip():
        print("  → Empty, skipping")
        processed_lines.append(line)
        continue
    
    latex_commands = re.findall(r'\\[a-zA-Z]+', line)
    print(f"  → Found {len(latex_commands)} commands: {latex_commands}")
    
    if len(latex_commands) == 0:
        print("  → No LaTeX, keep as-is")
        processed_lines.append(line)
    elif len(latex_commands) >= 3:
        stripped = line.strip()
        print(f"  → ≥3 commands, wrapping as display math")
        if not stripped.startswith('$$') and not stripped.startswith('$'):
            result = f'$$\n{stripped}\n$$'
            print(f"  → Result: {repr(result)}")
            processed_lines.append(result)
        else:
            processed_lines.append(line)
    else:
        print(f"  → 1-2 commands, inline wrapping")
        processed_lines.append(line)  # Simplified for debugging

text = '\n'.join(processed_lines)
print("\n" + "=" * 60)
print("FINAL RESULT:")
print(repr(text))
print()
print("VISUAL:")
print(text)
