# Sequences and Series

## Arithmetic Progression (AP)

### Core Formulas
- General term: aₙ = a + (n-1)d
- Sum of n terms: Sₙ = n/2 · [2a + (n-1)d] = n/2 · (a + l)  where l = last term
- Common difference: d = aₙ - aₙ₋₁
- Middle term of AP with n terms: a_{(n+1)/2} (for odd n)

### AP Identities
- If a, b, c are in AP: 2b = a + c
- Sum of first n natural numbers: Σk = n(n+1)/2
- Sum of squares: Σk² = n(n+1)(2n+1)/6
- Sum of cubes: Σk³ = [n(n+1)/2]²

## Geometric Progression (GP)

### Core Formulas
- General term: aₙ = a · rⁿ⁻¹
- Sum of n terms: Sₙ = a(rⁿ - 1)/(r - 1) for r ≠ 1; Sₙ = na for r = 1
- Sum to infinity (|r| < 1): S∞ = a/(1 - r)
- Common ratio: r = aₙ/aₙ₋₁

### GP Identities
- If a, b, c are in GP: b² = ac
- Geometric mean of a and b: GM = √(ab)
- Product of terms equidistant from ends = product of first and last term

## Arithmetic-Geometric Progression (AGP)

### Sum Formula for AGP
S = a, (a+d)r, (a+2d)r², (a+3d)r³, ...
**Method:** Let S = a + (a+d)r + (a+2d)r² + ...
Multiply by r: rS = ar + (a+d)r² + (a+2d)r³ + ...
Subtract: S(1-r) = a + dr + dr² + ... = a + dr/(1-r)
Therefore: **S = a/(1-r) + dr/(1-r)²** (for |r| < 1)

For finite AGP: use S - rS = algebraic sum, solve for S.

## Advanced Series Techniques

### Method of Differences
If Tₙ - Tₙ₋₁ = f(n) (a polynomial), use:
- Sₙ = T₁ + (T₂-T₁) + (T₃-T₂) + ... telescoping won't fully work
- Instead: if Tₙ is a polynomial in n, integrate or use known sums

### Vₙ Method (for partial fractions in series)
For series with terms like 1/[n(n+1)] or 1/[n(n+1)(n+2)]:
- 1/[n(n+1)] = 1/n - 1/(n+1)  → telescoping
- 1/[n(n+1)(n+2)] = ½[1/(n(n+1)) - 1/((n+1)(n+2))]  → telescoping
- General: 1/[n(n+1)...(n+k)] = [1/k] · [1/(n(n+1)...(n+k-1)) - 1/((n+1)(n+2)...(n+k))]

### Telescoping Series
If Tₙ = f(n) - f(n+1), then Sₙ = f(1) - f(n+1).
Key: identify Tₙ = Vₙ - Vₙ₊₁ form, then sum telescopes immediately.

### Sigma Notation Manipulation
- Σ(aₙ + bₙ) = Σaₙ + Σbₙ
- Σ(c·aₙ) = c·Σaₙ
- Σ from 1 to n of (n - k) = Σ from 1 to n of k (by symmetry substitution k → n-k)

## Worked Examples

### Example 1 (Standard): Sum of 1 + 3 + 5 + ... + (2n-1)
AP with a = 1, d = 2, last term = 2n-1.
n-th term: aₙ = 1 + (n-1)·2 = 2n - 1 ✓
Sum = n/2 · (1 + 2n-1) = n/2 · 2n = **n²**

### Example 2 (Tricky): Sum of series 1·2 + 2·3 + 3·4 + ... + n(n+1)
Tₙ = n(n+1) = n² + n
Sₙ = Σn² + Σn = n(n+1)(2n+1)/6 + n(n+1)/2 = n(n+1)/6 · [(2n+1) + 3] = **n(n+1)(n+2)/3**

### Example 3 (AGP): Sum of 1 + 2x + 3x² + 4x³ + ... (|x| < 1)
Let S = Σ(n+1)xⁿ from n=0 to ∞. Use AGP formula:
S = 1/(1-x)²

## JEE Traps
- AP middle term: use aₙ₋₁, aₙ₊₁ for terms around aₙ, not the index formula
- GP sum formula breaks at r = 1; handle separately (Sₙ = na)
- Infinite GP sum S∞ only valid when |r| < 1; always verify
- Sum of cubes: (Σk)² ≠ Σk² — common confusion
- AGP: don't try to use AP or GP sum formula; always use the S - rS method
- Telescoping: clearly write out first and last few terms to see what cancels

## Edge Cases
- If r = -1 in GP: terms oscillate, partial sums alternate; no infinite sum
- A single term is both an AP and GP
- For sum of first n terms of AP, if n is even, pair up first+last terms
