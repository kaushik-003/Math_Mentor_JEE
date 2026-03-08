# Derivatives

## Standard Derivatives Table

| f(x) | f'(x) |
|------|--------|
| xⁿ | n·x^(n-1) |
| eˣ | eˣ |
| aˣ | aˣ·ln(a) |
| ln(x) | 1/x |
| log_a(x) | 1/(x·ln a) |
| sin x | cos x |
| cos x | -sin x |
| tan x | sec²x |
| cot x | -csc²x |
| sec x | sec x·tan x |
| csc x | -csc x·cot x |
| sin⁻¹ x | 1/√(1-x²) |
| cos⁻¹ x | -1/√(1-x²) |
| tan⁻¹ x | 1/(1+x²) |
| cot⁻¹ x | -1/(1+x²) |
| sec⁻¹ x | 1/(|x|√(x²-1)) |
| √x | 1/(2√x) |

## Differentiation Rules

### Product Rule
(fg)' = f'g + fg'
Extension (Leibniz): (fg)^(n) = Σ C(n,k) f^(k) · g^(n-k)

### Quotient Rule
(f/g)' = (f'g - fg') / g²

### Chain Rule
d/dx[f(g(x))] = f'(g(x)) · g'(x)
For multiple composition: d/dx[f(g(h(x)))] = f'(g(h(x))) · g'(h(x)) · h'(x)

## Advanced Differentiation

### Implicit Differentiation
If F(x, y) = 0, then dy/dx = -∂F/∂x / ∂F/∂y
Or: differentiate both sides w.r.t. x, treat y as function of x (dy/dx appears).

Example: x² + y² = r² → 2x + 2y·(dy/dx) = 0 → dy/dx = -x/y

### Parametric Differentiation
If x = f(t), y = g(t), then:
dy/dx = (dy/dt) / (dx/dt) = g'(t) / f'(t)
d²y/dx² = d(dy/dx)/dt / (dx/dt) = [d(dy/dx)/dt] / f'(t)

### Logarithmic Differentiation
For y = f(x)^g(x), take ln both sides:
ln y = g(x)·ln(f(x))
Differentiate: (1/y)·(dy/dx) = g'(x)·ln(f(x)) + g(x)·f'(x)/f(x)
Multiply by y to get dy/dx.

Example: y = xˣ → ln y = x ln x → (1/y)y' = ln x + 1 → y' = xˣ(1 + ln x)

### Nth Derivatives of Standard Functions
- dⁿ/dxⁿ [eˣ] = eˣ
- dⁿ/dxⁿ [e^(ax)] = aⁿ·e^(ax)
- dⁿ/dxⁿ [sin(ax)] = aⁿ·sin(ax + nπ/2)
- dⁿ/dxⁿ [cos(ax)] = aⁿ·cos(ax + nπ/2)
- dⁿ/dxⁿ [xᵐ] = m!/(m-n)! · x^(m-n) for n ≤ m; 0 for n > m
- dⁿ/dxⁿ [ln x] = (-1)^(n-1)·(n-1)!/xⁿ  for n ≥ 1

## Worked Examples

### Example 1 (Standard): Differentiate y = x³·sin(x)
By product rule: y' = 3x²·sin(x) + x³·cos(x)

### Example 2 (Implicit): Find dy/dx for x³ + y³ = 3axy
Differentiate: 3x² + 3y²·(dy/dx) = 3a[y + x·(dy/dx)]
3y²·(dy/dx) - 3ax·(dy/dx) = 3ay - 3x²
(dy/dx)(3y² - 3ax) = 3ay - 3x²
**dy/dx = (ay - x²)/(y² - ax)**

### Example 3 (Logarithmic): Differentiate y = (sin x)^(cos x)
ln y = cos x · ln(sin x)
(1/y)·y' = -sin x · ln(sin x) + cos x · cos x/sin x
y' = (sin x)^(cos x) · [-sin x · ln(sin x) + cos²x/sin x]

## JEE Traps
- Chain rule: always multiply by the inner derivative — easy to forget
- d/dx[a^f(x)] = a^f(x) · ln(a) · f'(x), not just a^f(x)·f'(x)
- Implicit: when differentiating y², get 2y·(dy/dx), NOT just 2y
- Logarithmic differentiation: ln|y|, not ln(y), for negative values
- Product of 3 functions: extend product rule, (fgh)' = f'gh + fg'h + fgh'
- Parametric d²y/dx²: numerator is d(dy/dx)/dt, NOT d²y/dt², divided by dx/dt

## Edge Cases
- d/dx[|x|] = x/|x| = sgn(x), undefined at x = 0
- Derivative of constant = 0 always
- d/dx[x^(1/2)] = 1/(2√x), only valid for x > 0
- Implicit differentiation: result may contain both x and y, which is fine
