# Limits

## Standard Limits

### Fundamental Limits
- lim(x→0) sin(x)/x = 1
- lim(x→0) tan(x)/x = 1
- lim(x→0) (1 - cos x)/x² = 1/2
- lim(x→0) (aˣ - 1)/x = ln(a)
- lim(x→0) (eˣ - 1)/x = 1
- lim(x→0) ln(1 + x)/x = 1
- lim(x→∞) (1 + 1/x)^x = e
- lim(x→0) (1 + x)^(1/x) = e
- lim(x→0) (sin⁻¹ x)/x = 1
- lim(x→0) (tan⁻¹ x)/x = 1

## L'Hôpital's Rule

### When to Apply
Only for 0/0 or ∞/∞ indeterminate forms:
lim f(x)/g(x) = lim f'(x)/g'(x)  (if the latter limit exists)

### Indeterminate Forms and Transformations
| Form | Transform to |
|------|-------------|
| 0/0 | L'Hôpital directly |
| ∞/∞ | L'Hôpital directly |
| 0·∞ | Write as f/(1/g) or g/(1/f) → 0/0 or ∞/∞ |
| ∞ - ∞ | Combine fractions → 0/0 |
| 1^∞ | Write as e^[∞·ln(1)] = e^[0·∞] → e^[0/0] |
| 0^0 | Write as e^[0·ln(0)] = e^[0·(-∞)] → e^[∞/∞] |
| ∞^0 | Write as e^[0·ln(∞)] → same |

### 1^∞ Form: Key Formula
lim[f(x)]^g(x) where f → 1, g → ∞:
= exp(lim g(x)·[f(x) - 1])

Example: lim(1 + x/n)^n as n→∞ = e^x

## Taylor/Maclaurin Series for Limits

### Essential Expansions
- sin x = x - x³/6 + x⁵/120 - ... = Σ (-1)^n x^(2n+1)/(2n+1)!
- cos x = 1 - x²/2 + x⁴/24 - ... = Σ (-1)^n x^(2n)/(2n)!
- eˣ = 1 + x + x²/2 + x³/6 + ... = Σ xⁿ/n!
- ln(1 + x) = x - x²/2 + x³/3 - ... (for |x| ≤ 1, x ≠ -1)
- (1 + x)^n = 1 + nx + n(n-1)x²/2! + ... (for |x| < 1 if n not integer)
- tan x = x + x³/3 + 2x⁵/15 + ...
- sin⁻¹ x = x + x³/6 + 3x⁵/40 + ...
- tan⁻¹ x = x - x³/3 + x⁵/5 - ...

### Using Taylor Series for Limits
Substitute expansion, cancel leading terms, take limit.
Example: lim(x→0) (x - sin x)/x³
= lim(x→0) (x - [x - x³/6 + x⁵/120 - ...])/x³
= lim(x→0) (x³/6 - x⁵/120 + ...)/x³
= **1/6**

## Squeeze Theorem
If g(x) ≤ f(x) ≤ h(x) and lim g(x) = lim h(x) = L, then lim f(x) = L.

Classic: lim(x→0) x²·sin(1/x) = 0 because -x² ≤ x²sin(1/x) ≤ x² and lim x² = 0.

## Limits Involving Greatest Integer Function [x]
- [x] = floor(x) = largest integer ≤ x
- lim(x→n⁺) [x] = n,  lim(x→n⁻) [x] = n - 1
- [x] is discontinuous at all integers; left and right limits differ by 1

## Worked Examples

### Example 1 (Standard): lim(x→0) (e^(3x) - 1)/x
= lim(x→0) (e^(3x) - 1)/(3x) · 3 = 1 · 3 = **3**
(Using standard limit lim(t→0)(eᵗ-1)/t = 1 with t = 3x)

### Example 2 (Tricky — Taylor): lim(x→0) (1 - cos x - x²/2)/x⁴
cos x = 1 - x²/2 + x⁴/24 - ...
1 - cos x - x²/2 = 1 - (1 - x²/2 + x⁴/24 - ...) - x²/2 = -x⁴/24 + ...
Divide by x⁴: **-1/24**

### Example 3 (JEE Advanced — 1^∞): lim(x→0) (cos x)^(1/x²)
cos x → 1 as x → 0, and 1/x² → ∞.
Use formula: exp(lim [cos x - 1]/x²) = exp(lim(-x²/2)/x²) = exp(-1/2) = **e^(-1/2) = 1/√e**

## JEE Traps
- L'Hôpital: ONLY for 0/0 or ∞/∞ — applying it to 1/0 or 0^1 is wrong
- After applying L'Hôpital, check if the new limit is also indeterminate (may need multiple applications)
- lim(x→0) sin(x)/x = 1 only when x is in radians
- [x] limits: always check from left AND right at integer points
- 1^∞ form: use the exponential trick, not L'Hôpital directly
- Limits of composed functions: lim f(g(x)) = f(lim g(x)) only if f is continuous

## Edge Cases
- lim(x→0) x^x = 1 (0^0 form resolves to 1 via e^(x ln x) → e^0 = 1)
- lim(x→∞) x^(1/x) = 1 (∞^0 form)
- lim(x→0⁺) ln(x) = -∞  (left limit at 0 doesn't exist)
- Limits can exist even when function is undefined at that point
