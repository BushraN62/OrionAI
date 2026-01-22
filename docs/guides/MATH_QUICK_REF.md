# 📐 Math Rendering Quick Reference

## Syntax Summary

| Type | Syntax | Example Output |
|------|--------|---------------|
| **Inline** | `$equation$` | Text with $x^2$ inside |
| **Display** | `$$equation$$` | Centered block equation |

---

## Essential Commands

### Numbers & Variables
```latex
$x$, $y$, $z$           # Variables
$x_1$, $x_2$            # Subscripts  
$x^2$, $x^n$            # Superscripts
$x_i^2$                 # Combined
```

### Fractions & Roots
```latex
$\frac{a}{b}$           # Fraction
$\frac{x^2 + 1}{x - 1}$ # Complex fraction
$\sqrt{x}$              # Square root
$\sqrt[3]{x}$           # Cube root
```

### Greek Letters
```latex
$\alpha$ $\beta$ $\gamma$ $\delta$
$\epsilon$ $\theta$ $\lambda$ $\mu$
$\pi$ $\sigma$ $\phi$ $\omega$
$\Sigma$ $\Delta$ $\Omega$ $\Phi$
```

### Operators
```latex
$a + b - c$             # Addition, subtraction
$a \times b$            # Multiplication
$a \div b$              # Division
$a \pm b$               # Plus-minus
$a \cdot b$             # Dot product
$a \neq b$              # Not equal
$a \leq b$              # Less than or equal
$a \geq b$              # Greater than or equal
$a \approx b$           # Approximately equal
```

### Calculus
```latex
$\int f(x) dx$                    # Integral
$\int_a^b f(x) dx$                # Definite integral
$\frac{df}{dx}$                   # Derivative
$\frac{\partial f}{\partial x}$   # Partial derivative
$\lim_{x \to 0} f(x)$            # Limit
$\sum_{i=1}^{n} i$               # Sum
$\prod_{i=1}^{n} i$              # Product
```

### Sets & Logic
```latex
$\{1, 2, 3\}$           # Set
$x \in A$               # Element of
$A \cup B$              # Union
$A \cap B$              # Intersection
$A \subset B$           # Subset
$\emptyset$             # Empty set
$\forall x$             # For all
$\exists x$             # There exists
$P \implies Q$          # Implies
$P \iff Q$              # If and only if
```

### Functions
```latex
$\sin(x)$ $\cos(x)$ $\tan(x)$
$\log(x)$ $\ln(x)$ $\exp(x)$
$\max(x, y)$ $\min(x, y)$
```

### Matrices
```latex
$$\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}$$

$$\begin{pmatrix}
1 & 2 \\
3 & 4
\end{pmatrix}$$

$$\begin{vmatrix}
a & b \\
c & d
\end{vmatrix}$$
```

### Multi-line Equations
```latex
$$\begin{aligned}
x &= a + b \\
y &= c + d
\end{aligned}$$
```

### Piecewise Functions
```latex
$$f(x) = \begin{cases}
x^2 & \text{if } x \geq 0 \\
0 & \text{if } x < 0
\end{cases}$$
```

---

## Quick Examples

### Physics
```
$F = ma$
$E = mc^2$
$v = v_0 + at$
$\Delta x = v_0t + \frac{1}{2}at^2$
```

### Statistics
```
$\mu = \frac{1}{n}\sum_{i=1}^{n} x_i$
$\sigma = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(x_i - \mu)^2}$
$P(A|B) = \frac{P(B|A)P(A)}{P(B)}$
```

### Algebra
```
$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
$(a + b)^2 = a^2 + 2ab + b^2$
$a^m \cdot a^n = a^{m+n}$
```

### Trigonometry
```
$\sin^2(x) + \cos^2(x) = 1$
$e^{ix} = \cos(x) + i\sin(x)$
```

---

## Tips

✅ **Use inline math** for variables in sentences  
✅ **Use display math** for important equations  
✅ **Add spaces** around operators for clarity  
✅ **Use `\text{}`** for text inside equations  
✅ **Test syntax** at https://katex.org before using  

❌ **Don't** write math as plain text  
❌ **Don't** forget closing braces and dollar signs  
❌ **Don't** overuse display math for simple expressions  

---

## Test It!

Try asking Orion:
```
"Explain the quadratic formula"
"Show me the Pythagorean theorem"
"What's the derivative of x^2?"
"Explain Euler's formula"
```

---

**Full Guide:** See `docs/guides/MATH_RENDERING.md`  
**Test Page:** Open `ui/dashboard/math-test.html`
