# Definite Integrals

## Fundamental Theorem of Calculus

### FTC Part 1
If F(x) = ∫ₐˣ f(t) dt, then F'(x) = f(x)

### FTC Part 2
∫ₐᵇ f(x) dx = F(b) - F(a)  where F'(x) = f(x)

## Properties of Definite Integrals

### Basic Properties
- ∫ₐᵇ f(x) dx = -∫ᵦₐ f(x) dx
- ∫ₐᵃ f(x) dx = 0
- ∫ₐᵇ f(x) dx = ∫ₐᶜ f(x) dx + ∫ᶜᵇ f(x) dx  (additivity)
- ∫ₐᵇ [αf(x) + βg(x)] dx = α∫ₐᵇf dx + β∫ₐᵇg dx

### King's Property (Most Important JEE Property!)
∫ₐᵇ f(x) dx = ∫ₐᵇ f(a + b - x) dx

This is the **single most useful property for JEE**. Substitute x → a + b - x.

Example: ∫₀^(π/2) ln(sin x) dx = ∫₀^(π/2) ln(cos x) dx (let I = either one)
So 2I = ∫₀^(π/2) ln(sin x cos x) dx = ∫₀^(π/2) ln(sin 2x/2) dx
= ∫₀^(π/2) ln(sin 2x) dx - (π/2)ln 2 = I - (π/2)ln 2
Therefore I = **-(π/2)ln 2**

### Even/Odd Function Shortcuts
- If f is even (f(-x) = f(x)): ∫₋ₐᵃ f(x) dx = 2∫₀ᵃ f(x) dx
- If f is odd (f(-x) = -f(x)): ∫₋ₐᵃ f(x) dx = 0

### Period Property
If f has period T: ∫₀^(nT) f(x) dx = n·∫₀ᵀ f(x) dx

### Half-Interval Property
If f(a + x) = f(a - x) (symmetric about x = a):
∫₀^(2a) f(x) dx = 2∫₀ᵃ f(x) dx

If f(2a - x) = -f(x): ∫₀^(2a) f(x) dx = 0

## Leibniz Integral Rule
d/dx [∫_{a(x)}^{b(x)} f(t) dt] = f(b(x))·b'(x) - f(a(x))·a'(x)

Example: d/dx [∫ₓ^(x²) sin(t²) dt] = sin(x⁴)·2x - sin(x²)·1

## Estimation of Integrals

### Comparison Theorem
If f(x) ≤ g(x) on [a, b], then ∫ₐᵇf dx ≤ ∫ₐᵇg dx.

Bounds: if m ≤ f(x) ≤ M on [a,b], then m(b-a) ≤ ∫ₐᵇf dx ≤ M(b-a).

### Absolute Value Bound
|∫ₐᵇ f(x) dx| ≤ ∫ₐᵇ |f(x)| dx

## Gamma Function (Γ Function)
Γ(n) = ∫₀^∞ x^(n-1) e^(-x) dx for n > 0
- Γ(n) = (n-1)·Γ(n-1)
- Γ(n) = (n-1)! for positive integers n
- Γ(1/2) = √π
- Useful: ∫₀^∞ xⁿe^(-x) dx = n! = Γ(n+1)

## Worked Examples

### Example 1 (Standard): ∫₀² (x² + 1) dx
= [x³/3 + x]₀² = (8/3 + 2) - (0) = **14/3**

### Example 2 (King's Property): ∫₀^π x·sin x / (1 + cos²x) dx
Let I = ∫₀^π x·sin x / (1+cos²x) dx
By King's (a+b=π): I = ∫₀^π (π-x)·sin x / (1+cos²x) dx
Adding: 2I = π·∫₀^π sin x/(1+cos²x) dx = π·[tan⁻¹(-cos x)]₀^π
= π·[tan⁻¹(1) - tan⁻¹(-1)] = π·[π/4 + π/4] = π²/2
**I = π²/4**

### Example 3 (Leibniz): Find d/dx [∫₀^(x²) e^(t²) dt]
By Leibniz rule: e^((x²)²) · 2x = **2x·e^(x⁴)**

## JEE Traps
- King's property: substitute x → (a + b - x), the NEW integral must match pattern
- Even/odd check: carefully verify f(-x) before applying shortcuts
- Leibniz rule: don't forget the chain rule factor b'(x) or a'(x)
- Period property: requires the FULL function to have period T, not just pieces
- Switching limits changes sign: ∫ₐᵇ = -∫ᵦₐ — don't confuse with |∫|

## Edge Cases
- Improper integrals (limits → ∞ or integrand → ∞ at boundary): check convergence first
- ∫₋₁¹ 1/x dx diverges (NOT zero, despite odd function appearance; singularity at 0)
- If f has a finite number of discontinuities but is bounded, integral still exists
- Γ function extends factorial to non-integers; Γ(1/2) = √π is frequently useful in JEE
