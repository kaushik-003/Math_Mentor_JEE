# Integration Basics

## Standard Integrals Table

| ∫f(x)dx | Result |
|---------|--------|
| xⁿ (n ≠ -1) | x^(n+1)/(n+1) + C |
| 1/x | ln|x| + C |
| eˣ | eˣ + C |
| aˣ | aˣ/ln(a) + C |
| sin x | -cos x + C |
| cos x | sin x + C |
| sec²x | tan x + C |
| csc²x | -cot x + C |
| sec x tan x | sec x + C |
| csc x cot x | -csc x + C |
| 1/√(1-x²) | sin⁻¹x + C |
| -1/√(1-x²) | cos⁻¹x + C |
| 1/(1+x²) | tan⁻¹x + C |
| 1/√(x²-a²) | ln|x + √(x²-a²)| + C |
| 1/√(a²-x²) | sin⁻¹(x/a) + C |
| 1/(x²+a²) | (1/a)tan⁻¹(x/a) + C |
| √(a²-x²) | (x/2)√(a²-x²) + (a²/2)sin⁻¹(x/a) + C |

## Integration Techniques

### Substitution (u-substitution)
∫f(g(x))·g'(x)dx: let u = g(x), du = g'(x)dx → ∫f(u)du

Classic patterns:
- ∫f'(x)/f(x)dx = ln|f(x)| + C
- ∫f'(x)·[f(x)]ⁿdx = [f(x)]^(n+1)/(n+1) + C  for n ≠ -1

### Integration by Parts
∫u dv = uv - ∫v du
**ILATE rule** for choosing u: Inverse trig > Logarithm > Algebraic > Trig > Exponential
(Choose u as the type appearing earlier in ILATE)

Examples:
- ∫x·eˣ dx: u = x, dv = eˣdx → xeˣ - eˣ + C
- ∫ln x dx: u = ln x, dv = dx → x ln x - x + C
- ∫eˣ sin x dx: cyclic — integrate by parts twice, solve for the integral

### Partial Fractions
Decompose rational P(x)/Q(x) where deg(P) < deg(Q):

| Factor in Q(x) | Partial fraction form |
|---|---|
| (x - a) | A/(x - a) |
| (x - a)² | A/(x-a) + B/(x-a)² |
| (x² + px + q) irreducible | (Ax + B)/(x² + px + q) |
| (x² + px + q)² | (Ax+B)/(x²+px+q) + (Cx+D)/(x²+px+q)² |

If deg(P) ≥ deg(Q): do polynomial long division first.

### Trigonometric Substitutions
| Integrand contains | Substitute |
|---|---|
| √(a² - x²) | x = a sin θ |
| √(a² + x²) | x = a tan θ |
| √(x² - a²) | x = a sec θ |

### Trigonometric Integrals
- ∫sinⁿx cosᵐx dx: if n or m is odd, save one factor; use sin²+cos²=1
- If both even: use half-angle formulas sin²x = (1-cos2x)/2, cos²x = (1+cos2x)/2
- ∫sin(mx)cos(nx)dx: use product-to-sum formula

### Wallis Formula
∫₀^(π/2) sinⁿx dx = ∫₀^(π/2) cosⁿx dx
For even n: = [(n-1)(n-3)...3·1] / [n(n-2)...4·2] · π/2
For odd n:  = [(n-1)(n-3)...4·2] / [n(n-2)...5·3·1]

Example: ∫₀^(π/2) sin⁴x dx = (3·1)/(4·2) · π/2 = 3π/16

### Reduction Formulas
- ∫sinⁿx dx = -sinⁿ⁻¹x·cosx/n + (n-1)/n · ∫sinⁿ⁻²x dx
- ∫cosⁿx dx = cosⁿ⁻¹x·sinx/n + (n-1)/n · ∫cosⁿ⁻²x dx
- ∫xⁿeˣ dx = xⁿeˣ - n∫xⁿ⁻¹eˣ dx

## Worked Examples

### Example 1 (Standard): ∫x/(x²+1) dx
Let u = x²+1, du = 2x dx → (1/2)∫(1/u)du = (1/2)ln|x²+1| + C
= **(1/2)ln(x²+1) + C** (no absolute value needed since x²+1 > 0)

### Example 2 (Partial Fractions): ∫1/[(x-1)(x+2)] dx
1/[(x-1)(x+2)] = A/(x-1) + B/(x+2)
1 = A(x+2) + B(x-1)
x=1: 1 = 3A → A = 1/3. x=-2: 1 = -3B → B = -1/3.
∫[1/(3(x-1)) - 1/(3(x+2))]dx = **(1/3)ln|(x-1)/(x+2)| + C**

### Example 3 (By Parts — Cyclic): ∫eˣ sin x dx
Let I = ∫eˣ sin x dx
u = sin x, dv = eˣ dx → I = eˣ sin x - ∫eˣ cos x dx
Apply again: u = cos x, dv = eˣ dx → = eˣ sin x - [eˣ cos x + ∫eˣ sin x dx]
I = eˣ sin x - eˣ cos x - I
2I = eˣ(sin x - cos x)
**I = eˣ(sin x - cos x)/2 + C**

## JEE Traps
- Always add +C for indefinite integrals (even if answer is "clean")
- ∫1/x dx = ln|x| + C with absolute value — not just ln x
- ILATE rule: algebraic x beats exponential eˣ — put x as u in ∫xeˣdx
- Partial fractions: if numerator degree ≥ denominator degree, divide first
- Trig substitution: don't forget to convert back to x at the end (reverse substitute)
- Cyclic integration by parts: always check if the integral on the right matches I exactly

## Edge Cases
- ∫tan x dx = ln|sec x| + C = -ln|cos x| + C (both correct)
- ∫sec x dx = ln|sec x + tan x| + C (memorize this — no obvious derivation)
- ∫1/(x² - a²) dx = (1/2a)·ln|(x-a)/(x+a)| + C (partial fractions result)
- Integration constant C can differ in form but must be equivalent (check by differentiating)
