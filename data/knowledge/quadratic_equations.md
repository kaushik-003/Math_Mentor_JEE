# Quadratic Equations

## Core Formulas

### Quadratic Formula
For ax² + bx + c = 0 (a ≠ 0):
- x = (-b ± √(b² - 4ac)) / 2a
- Discriminant: D = b² - 4ac

### Nature of Roots (by Discriminant)
| D | Roots |
|---|-------|
| D > 0 | Two distinct real roots |
| D = 0 | Two equal real roots (x = -b/2a) |
| D < 0 | Two complex conjugate roots |
| D > 0 and perfect square | Two distinct rational roots |

### Vieta's Formulas
For roots α, β of ax² + bx + c = 0:
- α + β = -b/a
- αβ = c/a
- α - β = ±√D / a = ±√(b² - 4ac) / a
- α² + β² = (α + β)² - 2αβ = b²/a² - 2c/a
- α² · β² = (αβ)² = c²/a²

## Advanced Techniques

### Location of Roots on Number Line
For f(x) = ax² + bx + c with roots α ≤ β:

**Both roots > k:** D ≥ 0, f(k) > 0 (if a > 0), vertex x-coord (-b/2a) > k
**Both roots < k:** D ≥ 0, f(k) > 0 (if a > 0), -b/2a < k
**k lies between roots:** f(k) < 0 (if a > 0), equivalently a·f(k) < 0
**Exactly one root in (k₁, k₂):** f(k₁)·f(k₂) < 0

### Common Root Conditions
If ax² + bx + c = 0 and dx² + ex + f = 0 have a common root:
- Common root: x = (bf - ce)/(ae - bd) = (cd - af)/(bf - ce)
- Condition: (ae - bd)(bf - ce) = (cd - af)²

If both roots are common: a/d = b/e = c/f

### Equation Transformations
From ax² + bx + c = 0 with roots α, β, form equation with:
- Roots (α + k, β + k): substitute x → x - k → a(x-k)² + b(x-k) + c = 0
- Roots (1/α, 1/β): substitute x → 1/x → cx² + bx + a = 0
- Roots (kα, kβ): substitute x → x/k → ax² + kbx + k²c = 0
- Roots (α², β²): use (x - α²)(x - β²) = x² - (α²+β²)x + α²β²

### Sign Scheme (Wavy Curve Method)
For f(x) = a(x - r₁)(x - r₂) with r₁ < r₂:
- f(x) > 0 for x < r₁ or x > r₂ (when a > 0)
- f(x) < 0 for r₁ < x < r₂ (when a > 0)
- Always check open vs closed intervals based on >, ≥

### Maximum/Minimum of Quadratic
For f(x) = ax² + bx + c:
- Minimum at x = -b/2a (when a > 0), value = c - b²/4a = (4ac - b²)/4a
- Maximum at x = -b/2a (when a < 0), value = (4ac - b²)/4a
- Range: [(4ac-b²)/4a, ∞) if a > 0; (-∞, (4ac-b²)/4a] if a < 0

## Worked Examples

### Example 1 (Standard): Roots of 2x² - 7x + 3 = 0
- D = 49 - 24 = 25, √D = 5
- x = (7 ± 5)/4 → x = 3 or x = 1/2
- Check: α + β = 7/2, αβ = 3/2 ✓

### Example 2 (Tricky): Find k if x² - 5x + k = 0 has one root in (1, 2)
One root between 1 and 2 means f(1)·f(2) < 0:
- f(1) = 1 - 5 + k = k - 4
- f(2) = 4 - 10 + k = k - 6
- (k - 4)(k - 6) < 0 → **4 < k < 6**

### Example 3 (JEE Advanced): Find conditions for ax² + bx + c > 0 for all x
Requires: a > 0 and D < 0, i.e., b² - 4ac < 0

## JEE Traps
- Forgetting that D ≥ 0 is needed for real roots (D = 0 gives repeated root, still real)
- Using Vieta's without checking if roots are real — Vieta's applies to complex roots too
- Location of roots: always verify the vertex x-coord condition separately from D ≥ 0
- Transformation x → 1/x: if original has root 0, the transformed equation is different
- When checking both roots > 0: need D ≥ 0, sum > 0, AND product > 0 (all three)

## Edge Cases
- If a = 0: equation becomes linear, not quadratic
- Repeated root (D = 0): x = -b/2a is a double root; f(x) = a(x + b/2a)²
- Complex roots always come in conjugate pairs for real coefficients
- If c = 0: one root is always 0; other root is -b/a
