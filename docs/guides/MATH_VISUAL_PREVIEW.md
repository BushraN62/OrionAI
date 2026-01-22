# 🎨 Visual Preview: Math Rendering in Orion

## How It Looks

### 1. Inline Math Example

**Input:**
```markdown
Einstein's equation $E = mc^2$ revolutionized physics.
```

**Visual Appearance:**
```
Einstein's equation [E = mc²] revolutionized physics.
                     ↑         ↑
          Purple highlight  Rounded corners
```

**Styling:**
- Text flows naturally with equation inline
- Subtle purple background (rgba(99, 102, 241, 0.1))
- Purple border (1px, slightly transparent)
- Small padding for breathing room
- Matches surrounding text height

---

### 2. Display Math Example

**Input:**
```markdown
The quadratic formula:

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

This solves any quadratic equation.
```

**Visual Appearance:**
```
The quadratic formula:

┌────────────────────────────────────────┐
│                                        │
│         -b ± √(b² - 4ac)              │
│    x = ─────────────────               │
│              2a                        │
│                                        │
└────────────────────────────────────────┘
    ↑                              ↑
Dark background           Purple border
with box shadow          (glowing effect)

This solves any quadratic equation.
```

**Styling:**
- Centered on page
- Dark slate background (rgba(15, 23, 42, 0.6))
- Purple accent border (rgba(99, 102, 241, 0.3))
- Generous padding (1em all around)
- Rounded corners (0.75rem)
- Multi-layer shadow for depth
- Horizontal scroll if equation is too wide

---

## Color Palette

### Inline Math
```css
Background:  #6366f119  (purple at 10% opacity)
Border:      #6366f133  (purple at 20% opacity)
Text:        #e2e8f0    (slate-200)
```

### Display Math
```css
Background:  #0f172a99  (dark slate at 60% opacity)
Border:      #6366f14d  (purple at 30% opacity)
Text:        #e2e8f0    (slate-200)
Shadow:      Multiple layers with purple glow
```

### Scrollbar (for overflow)
```css
Track:       #0f172a66  (dark slate at 40% opacity)
Thumb:       #6366f166  (purple at 40% opacity)
Thumb Hover: #6366f199  (purple at 60% opacity)
```

---

## Real Examples

### Example 1: Simple Equation
```
The area of a circle is $A = \pi r^2$
```
**Renders as:** The area of a circle is [A = πr²]
                                          ↑_____↑
                                      Inline, purple

---

### Example 2: Complex Expression
```
$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$
```
**Renders as:**
```
┌────────────────────────────────────┐
│                                    │
│   ∞                   √π           │
│   ∫  e^(-x²) dx  =  ────           │
│   0                    2           │
│                                    │
└────────────────────────────────────┘
```

---

### Example 3: Matrix
```
$$\begin{bmatrix} a & b \\ c & d \end{bmatrix}$$
```
**Renders as:**
```
┌────────────────────────────────────┐
│                                    │
│           ┌       ┐                │
│           │ a  b  │                │
│           │ c  d  │                │
│           └       ┘                │
│                                    │
└────────────────────────────────────┘
```

---

### Example 4: Multi-line
```
$$\begin{aligned}
x &= a + b \\
y &= c + d
\end{aligned}$$
```
**Renders as:**
```
┌────────────────────────────────────┐
│                                    │
│         x = a + b                  │
│         y = c + d                  │
│                                    │
└────────────────────────────────────┘
```

---

## In Context (Chat Messages)

### User Message
```
┌────────────────────────────────────────┐
│ 👤 You                                 │
│                                        │
│ Can you explain the quadratic formula?│
└────────────────────────────────────────┘
```

### Orion's Response
```
┌────────────────────────────────────────┐
│ 🌟 Orion                               │
│                                        │
│ The quadratic formula solves equations│
│ of the form [ax² + bx + c = 0]. The  │
│ solution is given by:                  │
│                                        │
│ ┌──────────────────────────────────┐  │
│ │                                  │  │
│ │      -b ± √(b² - 4ac)           │  │
│ │  x = ─────────────────           │  │
│ │            2a                    │  │
│ │                                  │  │
│ └──────────────────────────────────┘  │
│                                        │
│ Where [a], [b], and [c] are the      │
│ coefficients from your equation.       │
│                                        │
│ Orchestrator • qwen2.5:7b             │
└────────────────────────────────────────┘
```

**Notice:**
- Inline math `[ax² + bx + c = 0]` has purple highlight
- Display math has centered dark box with purple border
- Inline variable references `[a]`, `[b]`, `[c]` are highlighted
- Clean, professional appearance
- Easy to read on dark background

---

## Size Comparison

### Inline Math
- Font size: 1.1em (110% of surrounding text)
- Compact, fits in line
- Minimal vertical space

### Display Math
- Font size: 1.1em (same clarity)
- Large padding makes it prominent
- Centered for emphasis
- Takes full width available

---

## Responsive Behavior

### Short Equations
- Display neatly within container
- Centered perfectly

### Long Equations
- Horizontal scrollbar appears automatically
- Container maintains height
- Scrollbar styled to match theme (purple)
- Equation stays readable

---

## Theme Integration

The math rendering seamlessly integrates with Orion's existing design:

1. **Color Scheme:** Purple accents match primary theme color
2. **Dark Mode:** Optimized for dark background
3. **Glass Morphism:** Uses similar blur and transparency effects
4. **Spacing:** Follows same padding/margin system
5. **Shadows:** Consistent depth effects
6. **Borders:** Same rounded corner style
7. **Typography:** Matches overall font sizing

---

## Browser Compatibility

✅ **Chrome/Edge:** Full support, smooth rendering  
✅ **Firefox:** Full support, smooth rendering  
✅ **Safari:** Full support, smooth rendering  
✅ **Mobile:** Touch-friendly scrolling for long equations  

---

## Accessibility

- **High Contrast:** White text on dark background (WCAG AAA)
- **Readable Fonts:** KaTeX uses clear, mathematical fonts
- **Scalable:** Respects browser zoom settings
- **Keyboard Navigation:** Scrollable with arrow keys
- **Screen Readers:** MathML support for accessibility

---

## Performance

- **Fast Rendering:** KaTeX is faster than MathJax
- **No Layout Shift:** Equations render in place
- **Cached Fonts:** KaTeX fonts load once
- **Minimal CSS:** Optimized selectors

---

## Try It Yourself!

### Open Test Page:
```powershell
start "w:\VS Code Projects\Orion  ( Qwen2.5 VL 7B )\ui\dashboard\math-test.html"
```

### Or Start Dashboard:
```powershell
cd "w:\VS Code Projects\Orion  ( Qwen2.5 VL 7B )\ui\dashboard"
npm run dev
```

### Then Try These Prompts:
1. "Show me the Pythagorean theorem"
2. "Explain Einstein's equation"
3. "What's the derivative of x cubed?"
4. "Display the quadratic formula"
5. "Show me a 2x2 matrix"

---

**Created:** November 10, 2025  
**See Also:**
- Full Guide: `docs/guides/MATH_RENDERING.md`
- Quick Reference: `docs/guides/MATH_QUICK_REF.md`
- Implementation: `docs/implementation/MATH_EQUATIONS_FRESH_START.md`
