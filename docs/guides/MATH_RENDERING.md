# Mathematical Equations in Orion Dashboard

## Overview

The Orion Dashboard fully supports rendering mathematical equations using **KaTeX**, a fast, easy-to-use JavaScript library for TeX math rendering on the web. This allows you to display beautiful, publication-quality mathematical expressions in your chat conversations.

## Quick Start

### Inline Math
Wrap your equation in single dollar signs to render it inline with text:

```
The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
```

**Result:** The quadratic formula is displayed inline within the sentence.

### Display Math
Wrap your equation in double dollar signs to render it as a centered block:

```
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

**Result:** The equation is displayed as a prominent centered block.

---

## Common LaTeX Syntax

### Basic Operations

| Description | LaTeX | Example |
|-------------|-------|---------|
| Superscript | `x^2` | $x^2$ |
| Subscript | `x_i` | $x_i$ |
| Fraction | `\frac{a}{b}` | $\frac{a}{b}$ |
| Square root | `\sqrt{x}` | $\sqrt{x}$ |
| Nth root | `\sqrt[n]{x}` | $\sqrt[n]{x}$ |

### Greek Letters

| Letter | LaTeX | Letter | LaTeX |
|--------|-------|--------|-------|
| α | `\alpha` | β | `\beta` |
| γ | `\gamma` | δ | `\delta` |
| ε | `\epsilon` | θ | `\theta` |
| λ | `\lambda` | μ | `\mu` |
| π | `\pi` | σ | `\sigma` |
| Σ | `\Sigma` | Δ | `\Delta` |

### Calculus

```latex
# Integral
$$\int_a^b f(x) dx$$

# Partial derivative
$$\frac{\partial f}{\partial x}$$

# Limit
$$\lim_{x \to \infty} f(x)$$

# Sum
$$\sum_{i=1}^{n} i$$

# Product
$$\prod_{i=1}^{n} i$$
```

### Linear Algebra

```latex
# Matrix
$$\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}$$

# Determinant
$$\det(A) = \begin{vmatrix}
a & b \\
c & d
\end{vmatrix}$$

# Vector
$$\vec{v} = \langle x, y, z \rangle$$

# Dot product
$$\vec{a} \cdot \vec{b}$$

# Cross product
$$\vec{a} \times \vec{b}$$
```

### Logic and Set Theory

```latex
# Set notation
$$A = \{x \mid x > 0\}$$

# Union and intersection
$$A \cup B \quad A \cap B$$

# Subset and element
$$A \subseteq B \quad x \in A$$

# For all and exists
$$\forall x \in A \quad \exists y \in B$$

# Implies and iff
$$P \implies Q \quad P \iff Q$$
```

---

## Real-World Examples

### 1. Physics: Newton's Second Law
```
Newton's second law states that $F = ma$, or in full form:

$$F = m \frac{d^2x}{dt^2}$$
```

### 2. Statistics: Normal Distribution
```
The probability density function of a normal distribution is:

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$

where $\mu$ is the mean and $\sigma$ is the standard deviation.
```

### 3. Computer Science: Big O Notation
```
The time complexity of merge sort is $O(n \log n)$, which can be proven by:

$$T(n) = 2T\left(\frac{n}{2}\right) + O(n)$$
```

### 4. Calculus: Taylor Series
```
The Taylor series expansion of $e^x$ around $x = 0$ is:

$$e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots$$
```

### 5. Linear Algebra: Eigenvalues
```
The eigenvalues $\lambda$ of a matrix $A$ satisfy:

$$\det(A - \lambda I) = 0$$

where $I$ is the identity matrix.
```

---

## Advanced Features

### Multi-line Equations

Use the `aligned` environment for multi-line equations:

```latex
$$\begin{aligned}
x &= a + b \\
y &= c + d \\
z &= e + f
\end{aligned}$$
```

### Cases (Piecewise Functions)

```latex
$$f(x) = \begin{cases}
x^2 & \text{if } x \geq 0 \\
-x^2 & \text{if } x < 0
\end{cases}$$
```

### Systems of Equations

```latex
$$\begin{cases}
x + y = 5 \\
2x - y = 1
\end{cases}$$
```

---

## Styling in Orion

### Inline Math Appearance
- Subtle purple background highlight
- Rounded corners
- Slightly smaller than display math
- Vertically aligned with text

### Display Math Appearance
- Centered on the page
- Dark background with purple accent border
- Shadow effect for depth
- Horizontal scrollbar for long equations
- Larger, more prominent text

---

## Tips and Best Practices

### ✅ Do's

1. **Use display math for important equations**
   - Makes them stand out
   - Easier to read
   - Better for complex expressions

2. **Use inline math for quick references**
   - Variables: $x$, $y$, $z$
   - Simple expressions: $a + b$
   - Constants: $\pi$, $e$

3. **Add context with text**
   - Explain what variables mean
   - Provide units
   - Give examples

4. **Break down complex equations**
   - Show step-by-step derivations
   - Use multiple display blocks
   - Add explanatory text between steps

### ❌ Don'ts

1. **Don't use regular text for math**
   - ❌ Write "x^2" as plain text
   - ✅ Use $x^2$ instead

2. **Don't overuse display math**
   - Save it for important equations
   - Use inline math for simple expressions

3. **Don't forget spacing**
   - Add spaces around operators
   - Use `\quad` or `\qquad` for extra space
   - Example: $a \quad b$ vs $ab$

---

## Troubleshooting

### Equation Not Rendering?

**Check your syntax:**
- Ensure you have matching dollar signs
- Verify all braces are closed `{}`
- Check for typos in command names

**Common mistakes:**
```latex
❌ $$\frac{a}{b  # Missing closing brace and $$
✅ $$\frac{a}{b}$$

❌ $x^2 + y^2$  # This is fine for simple cases
✅ $x^2 + y^2$  # But use \\ for line breaks in display mode
```

### Equation Cut Off?

For very long equations, the display block will scroll horizontally. You can also:
- Break it into multiple lines using `\\`
- Use the `aligned` environment
- Simplify the expression

### Special Characters

To display special characters, escape them:
- Dollar sign: `\$`
- Percent: `\%`
- Ampersand: `\&`
- Underscore: `\_`

---

## Testing Your Equations

### Option 1: Use the Test Page
Open `math-test.html` in your browser to see example equations rendered.

### Option 2: Online KaTeX Editor
Visit https://katex.org/ to test your LaTeX syntax before using it in Orion.

### Option 3: Ask Orion
Simply ask Orion to explain mathematical concepts, and it will use proper equation formatting!

---

## Technical Details

### Libraries Used
- **KaTeX 0.16.25** - Fast math rendering engine
- **remark-math** - Parses math in Markdown
- **rehype-katex** - Renders math with KaTeX

### CSS Classes
- `.katex` - Base KaTeX container
- `.katex-display` - Display mode equations
- `.katex-html` - HTML rendering of math

### Configuration
Math rendering is automatically configured in `ChatPanel.tsx`:
```typescript
<ReactMarkdown
  remarkPlugins={[remarkMath]}
  rehypePlugins={[rehypeKatex, rehypeHighlight]}
>
  {content}
</ReactMarkdown>
```

---

## Examples to Try in Orion

Copy and paste these into the Orion chat to see them rendered:

```
Can you explain Einstein's equation? $E = mc^2$

Show me the quadratic formula:
$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

What's the integral of $x^2$?

Explain the Pythagorean theorem: $a^2 + b^2 = c^2$

Show me Maxwell's equations in differential form:
$$\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}$$
$$\nabla \cdot \mathbf{B} = 0$$
$$\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$$
$$\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}$$
```

---

## Resources

- **KaTeX Documentation:** https://katex.org/docs/supported.html
- **LaTeX Math Symbols:** https://www.cmor-faculty.rice.edu/~heinken/latex/symbols.pdf
- **Detexify:** https://detexify.kirelabs.org/classify.html (Draw a symbol to find its LaTeX command)

---

## Support

If you encounter any issues with math rendering:
1. Check this documentation
2. Test your LaTeX syntax on https://katex.org/
3. Check the browser console for errors
4. Verify KaTeX CSS is loaded in `index.css`

Happy calculating! 🚀✨
