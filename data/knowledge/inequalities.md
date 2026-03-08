# Inequalities

## Core Inequalities

### AM-GM Inequality
For non-negative reals a₁, a₂, ..., aₙ:
(a₁ + a₂ + ... + aₙ)/n ≥ (a₁·a₂·...·aₙ)^(1/n)
**Equality holds iff a₁ = a₂ = ... = aₙ**

Common applications:
- a + b ≥ 2√(ab) for a, b ≥ 0
- a + 1/a ≥ 2 for a > 0
- x² + y² ≥ 2xy  (equivalently (x-y)² ≥ 0)
- (a + b)(c + d) ≥ (√(ac) + √(bd))² ? No — use AM-GM directly

### Cauchy-Schwarz Inequality
(a₁² + a₂² + ... + aₙ²)(b₁² + b₂² + ... + bₙ²) ≥ (a₁b₁ + a₂b₂ + ... + aₙbₙ)²
**Equality: a₁/b₁ = a₂/b₂ = ... = aₙ/bₙ**

Useful form: (a² + b²)(c² + d²) ≥ (ac + bd)²

### Triangle Inequality
|a + b| ≤ |a| + |b|
|a - b| ≥ ||a| - |b||
Also: |x - y| ≥ |x| - |y|

### Weighted AM-GM
For positive weights w₁, w₂ (with w₁ + w₂ = 1) and positive a, b:
w₁a + w₂b ≥ a^(w₁) · b^(w₂)
Equality: a = b

### Chebyshev's Sum Inequality
If a₁ ≥ a₂ ≥ ... ≥ aₙ and b₁ ≥ b₂ ≥ ... ≥ bₙ (same order), then:
n·(Σaᵢbᵢ) ≥ (Σaᵢ)(Σbᵢ)
If they are in opposite order: n·(Σaᵢbᵢ) ≤ (Σaᵢ)(Σbᵢ)

### Power Mean Inequality
For p > q: M_p ≥ M_q where M_p = [(Σaᵢᵖ)/n]^(1/p)
Hierarchy: max ≥ HM ≥ GM ≥ AM (wait: AM ≥ GM ≥ HM)
**Correct: AM ≥ GM ≥ HM** where HM = n/(1/a₁ + ... + 1/aₙ)

## Solving Quadratic Inequalities

### Wavy Curve (Sign Chart) Method
For f(x) = (x - a₁)^m₁ · (x - a₂)^m₂ · ... (ordered a₁ < a₂ < ...):
1. Mark roots on number line
2. Rightmost region: sign = sign of leading coefficient
3. At each root: flip sign if multiplicity mᵢ is odd; same sign if mᵢ is even
4. Read off where f > 0 or f < 0

Example: x(x-2)²(x+1) > 0
Roots: -1 (odd mult), 0 (odd mult), 2 (even mult)
Rightmost: + (positive for large x)
x > 2: +; passing x=2 (even, no flip): +; 0 < x < 2: flip at 0 → -; -1 < x < 0: flip at -1 → +; x < -1: flip → -
Solution: x ∈ (-1, 0) ∪ (2, ∞)  [strict inequality, exclude roots]

## Advanced Techniques

### Using Calculus for Inequalities
To prove f(x) ≥ g(x): let h(x) = f(x) - g(x), show h(x) ≥ 0 by:
1. Find h'(x) = 0 to get critical points
2. Check h''(x) at critical points (minimum if h'' > 0)
3. Verify h(minimum point) ≥ 0

### Optimization via AM-GM
**Strategy:** Write expression as sum of terms, apply AM-GM to get lower bound.
Key trick: split terms strategically so the "equal" condition gives a valid point.

Example: Minimize x + 1/x for x > 0:
x + 1/x ≥ 2√(x · 1/x) = 2. Equality at x = 1. Minimum = 2.

Example: Minimize x² + y² given x + y = 1:
x² + y² = (x+y)² - 2xy = 1 - 2xy. Maximize xy with x+y=1: xy ≤ (x+y)²/4 = 1/4.
So x² + y² ≥ 1 - 1/2 = **1/2**.

## Worked Examples

### Example 1 (Standard): Solve x² - 5x + 6 > 0
Factor: (x-2)(x-3) > 0
Wavy curve: roots at 2, 3; both simple (odd multiplicity)
Rightmost region: +. At x=3: flip → -. At x=2: flip → +.
**Solution: x < 2 or x > 3**

### Example 2 (Tricky — Cauchy-Schwarz): Prove (a+b+c)² ≤ 3(a²+b²+c²)
By Cauchy-Schwarz with (1,1,1) and (a,b,c):
(1²+1²+1²)(a²+b²+c²) ≥ (a+b+c)²
→ 3(a²+b²+c²) ≥ (a+b+c)²  ✓

## JEE Traps
- AM-GM requires ALL terms non-negative; check domain before applying
- Equality condition: for AM-GM to achieve equality, ALL terms must be equal
- Cauchy-Schwarz equality: ratios must be equal, not the terms themselves
- When flipping inequality: multiplying/dividing by negative number flips sign
- Squaring inequality: only valid when both sides are non-negative
- Wavy curve: even multiplicity roots do NOT change sign; easy to forget

## Edge Cases
- For |f(x)| < k: equivalent to -k < f(x) < k (open interval, k > 0)
- For |f(x)| > k: equivalent to f(x) < -k OR f(x) > k
- AM-GM with zero: if any term is 0, GM = 0, and AM = (sum)/n ≥ 0 trivially
- Always check if inequality is strict (>, <) or non-strict (≥, ≤) for endpoints
