# 📐 Mathematical Equations Support

Complete implementation of beautiful, publication-quality mathematical equation rendering in the Orion Dashboard using KaTeX.

---

## 🚀 Quick Start

### View Examples
Open the test page to see all features:
```powershell
start "w:\VS Code Projects\Orion  ( Qwen2.5 VL 7B )\ui\dashboard\math-test.html"
```

### Use in Chat
Just wrap math in dollar signs:

**Inline:** `$E = mc^2$`  
**Display:** `$$\int_0^1 x^2 dx$$`

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[MATH_RENDERING.md](./MATH_RENDERING.md)** | Complete guide with syntax, examples, and best practices |
| **[MATH_QUICK_REF.md](./MATH_QUICK_REF.md)** | One-page cheat sheet for quick reference |
| **[MATH_VISUAL_PREVIEW.md](./MATH_VISUAL_PREVIEW.md)** | Visual examples showing how equations look |
| **[MATH_EQUATIONS_FRESH_START.md](../implementation/MATH_EQUATIONS_FRESH_START.md)** | Implementation details and technical notes |

---

## ✨ Features

✅ **Inline math** - equations within text (`$x^2$`)  
✅ **Display math** - centered blocks (`$$\frac{a}{b}$$`)  
✅ **Full LaTeX support** - fractions, roots, integrals, matrices  
✅ **Greek letters** - α, β, γ, δ, Σ, Ω  
✅ **Calculus notation** - derivatives, integrals, limits, sums  
✅ **Linear algebra** - matrices, vectors, determinants  
✅ **Custom styling** - purple theme matching Orion dashboard  
✅ **Dark mode optimized** - high contrast, readable  
✅ **Horizontal scrolling** - for long equations  
✅ **Fast rendering** - powered by KaTeX  

---

## 🎨 Visual Style

### Inline Math
- Subtle purple background highlight
- Rounded corners with border
- Flows naturally with text
- Example: The equation $x^2 + y^2 = z^2$ is the Pythagorean theorem.

### Display Math
- Centered block with dark background
- Purple accent border with glow
- Generous padding and spacing
- Example:
  $$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$

---

## 📖 Common Syntax

```latex
# Fractions
$\frac{a}{b}$

# Superscripts/Subscripts
$x^2$, $x_i$

# Square Root
$\sqrt{x}$

# Integrals
$\int_a^b f(x) dx$

# Sums
$\sum_{i=1}^{n} i$

# Greek Letters
$\alpha$, $\beta$, $\gamma$

# Matrices
$$\begin{bmatrix} a & b \\ c & d \end{bmatrix}$$
```

---

## 🧪 Testing

### 1. Open Test Page
Interactive demonstrations of all features:
```powershell
start math-test.html
```

### 2. Run Dashboard
```powershell
cd ui/dashboard
npm run dev
```

### 3. Try Examples
Ask Orion:
- "Explain the quadratic formula"
- "Show me Einstein's equation"
- "What's the Pythagorean theorem?"

---

## 🔧 Technical Stack

```json
{
  "katex": "^0.16.25",
  "react-markdown": "^10.1.0",
  "remark-math": "^6.0.0",
  "rehype-katex": "^7.0.1"
}
```

**Files:**
- `src/index.css` - Custom KaTeX styling
- `src/components/ChatPanel.tsx` - ReactMarkdown configuration
- `math-test.html` - Interactive test page

---

## 📋 Quick Examples to Try

```markdown
1. Einstein: $E = mc^2$

2. Quadratic: $$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

3. Pythagorean: $a^2 + b^2 = c^2$

4. Calculus: $\frac{d}{dx}x^2 = 2x$

5. Statistics: $\mu = \frac{1}{n}\sum_{i=1}^{n} x_i$

6. Matrix: $$\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}$$

7. Integral: $$\int_0^1 x^2 dx = \frac{1}{3}$$

8. Limit: $$\lim_{x \to 0} \frac{\sin x}{x} = 1$$
```

---

## 🎯 Best Practices

### ✅ Do
- Use display math for important equations
- Use inline math for variables in text
- Add context and explanations
- Test complex syntax at https://katex.org
- Break down multi-step derivations

### ❌ Don't
- Write math as plain text
- Overuse display math
- Forget closing braces
- Skip explanatory text
- Use unsupported LaTeX commands

---

## 🆘 Troubleshooting

**Equation not rendering?**
- Check matching dollar signs
- Verify all braces are closed
- Test syntax at katex.org
- Check browser console for errors

**Equation cut off?**
- Horizontal scroll automatically appears
- Break into multiple lines with `\\`
- Use `aligned` environment

**Special characters?**
- Escape with backslash: `\$`, `\%`, `\&`

---

## 📚 Resources

- **KaTeX Docs:** https://katex.org/docs/supported.html
- **LaTeX Symbols:** https://www.cmor-faculty.rice.edu/~heinken/latex/symbols.pdf
- **Detexify:** https://detexify.kirelabs.org/classify.html (draw symbols)
- **Test Page:** `ui/dashboard/math-test.html`

---

## 🎉 Status

✅ **Complete and Ready to Use**

All math rendering features are fully implemented, tested, and documented. Start using math in your Orion conversations today!

---

**Created:** November 10, 2025  
**Version:** 1.0.0  
**Status:** Production Ready
