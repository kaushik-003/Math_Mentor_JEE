# Applications of Derivatives

## Maxima and Minima

### First Derivative Test
At a critical point c where f'(c) = 0:
- f'changes + to -: local maximum at c
- f'changes - to +: local minimum at c
- f'doesn't change sign: neither (inflection point)

### Second Derivative Test
At f'(c) = 0:
- f''(c) < 0: local maximum
- f''(c) > 0: local minimum
- f''(c) = 0: inconclusive — go back to first derivative test

### Global Extrema on [a, b]
1. Find all critical points c where f'(c) = 0 in (a, b)
2. Evaluate f at all critical points + endpoints a and b
3. Largest value = global max; smallest = global min

## Increasing/Decreasing Functions

f is increasing on I if f'(x) > 0 for all x ∈ I
f is decreasing on I if f'(x) < 0 for all x ∈ I

**Procedure:**
1. Find f'(x)
2. Solve f'(x) = 0 for critical points
3. Test sign of f'(x) in each interval
4. Report increasing/decreasing intervals

## Mean Value Theorems

### Rolle's Theorem
If f is continuous on [a,b], differentiable on (a,b), and f(a) = f(b):
∃ c ∈ (a, b) such that f'(c) = 0

### Lagrange Mean Value Theorem (LMVT)
If f is continuous on [a,b] and differentiable on (a,b):
∃ c ∈ (a, b) such that **f'(c) = [f(b) - f(a)] / (b - a)**

Geometric meaning: slope of tangent = slope of chord at some interior point.

Applications of LMVT:
- Proving inequalities: e.g., prove ln(1+x) < x for x > 0
  f(t) = ln t on [1, 1+x], LMVT gives ln(1+x) - 0 = 1/c · x for some c ∈ (1, 1+x)
  Since c > 1, 1/c < 1, so ln(1+x) = x/c < x ✓

## Tangent and Normal to a Curve

At point (x₀, y₀) on y = f(x):
- **Tangent slope:** m = f'(x₀)
- **Tangent equation:** y - y₀ = f'(x₀)(x - x₀)
- **Normal slope:** -1/f'(x₀)  (perpendicular to tangent)
- **Normal equation:** y - y₀ = [-1/f'(x₀)](x - x₀)

If f'(x₀) = 0: tangent is horizontal y = y₀; normal is vertical x = x₀
If f'(x₀) = ∞: tangent is vertical; normal is horizontal

## Concavity and Inflection Points

- f''(x) > 0 on I: f is concave up (bowl-shaped ∪) on I
- f''(x) < 0 on I: f is concave down (cap-shaped ∩) on I
- **Inflection point:** where f'' changes sign (concavity changes)

Note: f''(c) = 0 is necessary but NOT sufficient for inflection — must check sign change.

## Optimization with Constraints

### Method: Substitution
1. Write objective function f(x, y)
2. Use constraint to express y in terms of x
3. Substitute → single-variable optimization

### Method: AM-GM or Cauchy-Schwarz
For symmetric problems, use inequalities directly to find the minimum.

### Optimization Steps
1. Define variables and write objective function
2. Identify constraint(s)
3. Reduce to single variable (substitution or Lagrange multipliers)
4. Differentiate, set = 0, solve
5. Verify it's max/min using second derivative or boundary check

## Worked Examples

### Example 1 (Standard): Minimum value of x + 1/x for x > 0
f'(x) = 1 - 1/x² = 0 → x² = 1 → x = 1 (positive root)
f''(1) = 2/x³|₁ = 2 > 0 → local (and global) minimum
**Minimum = f(1) = 1 + 1 = 2**

### Example 2 (Tricky — LMVT application): Prove sin x < x for all x > 0
Let f(t) = sin t on [0, x]. By LMVT: (sin x - sin 0)/(x - 0) = cos c for some c ∈ (0, x).
sin x / x = cos c < 1 (since c > 0)
Therefore **sin x < x** for all x > 0. ✓

### Example 3 (JEE Advanced — Constrained Optimization): Rectangle inscribed in ellipse x²/a² + y²/b² = 1
Vertices at (x, y), area = 4xy. Maximize subject to x²/a² + y²/b² = 1.
Let x = a cos t, y = b sin t. Area = 4ab sin t cos t = 2ab sin 2t.
Maximum at sin 2t = 1 → t = π/4 → x = a/√2, y = b/√2.
**Maximum area = 2ab**

## JEE Traps
- Critical point ≠ local extremum: check sign change of f' (or use f'')
- f''(c) = 0 does not mean inflection point — must verify f'' changes sign
- Global max/min: always check endpoints for closed interval problems
- Rolle's theorem requires f(a) = f(b): don't apply without checking this
- LMVT: c is in OPEN interval (a,b), not the endpoints
- Tangent at corner/cusp: derivative doesn't exist; tangent is undefined

## Edge Cases
- Constant function: f'(x) = 0 everywhere, but no extrema (every point is max and min)
- If f'(x) = 0 only at isolated points but doesn't change sign: not an extremum
- Vertical tangent: occurs when f'(x₀) → ±∞; curve has infinite slope at that point
