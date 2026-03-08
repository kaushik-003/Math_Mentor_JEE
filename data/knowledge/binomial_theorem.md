# Binomial Theorem

## Core Formulas

### Binomial Expansion
(a + b)ⁿ = Σ C(n,r) · aⁿ⁻ʳ · bʳ  for r = 0 to n

Where C(n,r) = nCr = n! / (r!(n-r)!)

### General Term
T_{r+1} = C(n,r) · aⁿ⁻ʳ · bʳ  (the (r+1)th term)

### Middle Term
- If n is even: middle term is T_{n/2 + 1}
- If n is odd: two middle terms T_{(n+1)/2} and T_{(n+3)/2}

### Properties of Binomial Coefficients
- C(n,0) = C(n,n) = 1
- C(n,r) = C(n, n-r)  (symmetry)
- C(n,r) + C(n,r+1) = C(n+1, r+1)  (Pascal's identity)
- ΣC(n,r) = 2ⁿ  (sum of all coefficients)
- ΣC(n,r) for even r = ΣC(n,r) for odd r = 2ⁿ⁻¹
- Σr·C(n,r) = n·2ⁿ⁻¹
- Σr²·C(n,r) = n(n+1)·2ⁿ⁻²

## Advanced Techniques

### Finding Coefficient of xᵏ in Expansion
1. Write general term T_{r+1} = C(n,r) · (first part)^(n-r) · (second part)^r
2. Find the power of x in T_{r+1} as a function of r
3. Set power = k, solve for r (must be non-negative integer)
4. Substitute r to find the coefficient

Example: Coefficient of x³ in (2x - 1/x)⁷
- T_{r+1} = C(7,r)·(2x)^(7-r)·(-1/x)^r = C(7,r)·2^(7-r)·(-1)^r · x^(7-r-r)
- Power of x: 7 - 2r = 3 → r = 2
- Coefficient: C(7,2)·2⁵·(-1)² = 21·32 = **672**

### Multinomial Theorem
(x₁ + x₂ + ... + xₖ)ⁿ = Σ [n!/(r₁!r₂!...rₖ!)] · x₁^r₁ · x₂^r₂ · ... · xₖ^rₖ
where r₁ + r₂ + ... + rₖ = n

Number of terms = C(n+k-1, k-1)

### Binomial Approximation (for |x| << 1)
- (1 + x)ⁿ ≈ 1 + nx  for small x
- (1 + x)^(1/2) ≈ 1 + x/2 - x²/8 + ...
- (1 - x)^(-1) ≈ 1 + x + x² + x³ + ...

### Divisibility Using Binomial
To show N is divisible by m²: write N = (1 + m)ⁿ - 1, expand, first two terms cancel,
remaining terms all contain m².

Example: Show (1 + 7)⁹ - 1 = 8⁹ - 1 is divisible by 49:
(1+7)⁹ - 1 = 9·7 + C(9,2)·49 + ... = 63 + 49k = 7(9 + 7k') — wait, need mod 49:
= 9·7 + C(9,2)·7² + higher = 63 + 49·36 + ... ≡ 63 ≡ 63 - 49 = 14 (mod 49)
Actually: (8⁹ - 1) = (1+7)⁹ - 1 = 63 + 49·[C(9,2) + 7·C(9,3) + ...]
The last bracket is an integer, so 8⁹ - 1 = 63 + 49m → not divisible by 49.
But 8⁹ - 1 is divisible by 7 since 8 ≡ 1 (mod 7).

### Greatest Term in Expansion
For (1 + x)ⁿ, T_{r+1}/T_r = (n-r+1)/r · x
Find r where T_{r+1}/T_r ≥ 1, i.e., r ≤ (n+1)x/(1+x)
Greatest term index: r = floor[(n+1)x/(1+x)] or that value if integer.

## Worked Examples

### Example 1 (Standard): Expand (x + 2)⁴
T_{r+1} = C(4,r)·x^(4-r)·2^r
- r=0: C(4,0)x⁴·1 = x⁴
- r=1: C(4,1)x³·2 = 8x³
- r=2: C(4,2)x²·4 = 24x²
- r=3: C(4,3)x·8 = 32x
- r=4: C(4,4)·16 = 16
Result: **(x+2)⁴ = x⁴ + 8x³ + 24x² + 32x + 16**

### Example 2 (Tricky JEE): Find term independent of x in (x² + 1/x)⁹
T_{r+1} = C(9,r)·(x²)^(9-r)·(1/x)^r = C(9,r)·x^(18-2r-r) = C(9,r)·x^(18-3r)
For constant term: 18 - 3r = 0 → r = 6
Answer: C(9,6) = C(9,3) = **84**

## JEE Traps
- General term index: T_{r+1}, not T_r — plug r=0 to get first term, r=1 for second
- Middle term: check if n is even (one middle term) or odd (two middle terms)
- When finding coefficient of xᵏ: set power of x equal to k, solve for r — verify r is integer
- Sum of coefficients: substitute x = 1 (not x = 0) in the expansion
- For (a - b)ⁿ: the sign alternates as (-1)^r, easy to forget

## Edge Cases
- (1 + x)ⁿ for non-integer n (infinite series): valid only for |x| < 1
- If r is not an integer, there is no term with that power of x
- C(n, r) = 0 when r > n or r < 0 — expansion automatically terminates
