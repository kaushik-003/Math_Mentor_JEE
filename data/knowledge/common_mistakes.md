# Common JEE Mistakes and Traps

## Algebra Mistakes

### Sign Errors
- (a - b)² = a² - 2ab + b²  (NOT a² + b²)
- (a + b)³ ≠ a³ + b³  (missing 3a²b + 3ab² terms)
- When moving term to other side: change sign (x + 3 = 5 → x = 2, not x = 8)
- Forgetting ± in: quadratic formula, √ of both sides, |x| = k gives x = ±k

### Quadratic and Root Errors
- **Forgetting to check denominator = 0 after solving**: e.g., solving 1/(x-2) = 3 gives x = 7/3; check x ≠ 2 ✓
- **Root of both sides**: x² = 4 → x = ±2, NOT just x = 2
- **Extraneous roots**: squaring both sides can introduce false solutions; always verify in original
- **Discriminant**: D = b² - 4ac, not b² + 4ac or b² - 2ac

## Calculus Mistakes

### Limits
- **Applying L'Hôpital to non-indeterminate forms**: lim(x→0) x/sin(x) is NOT 0/0 type when x→1 say — check the form first
- **L'Hôpital gives wrong answer** when new limit doesn't exist but original does (e.g., lim sin(x)/x as x→∞)
- **Forgetting series expansion is faster**: for limits like lim (x - sin x)/x³, series is cleaner than repeated L'Hôpital
- **lim sin(x)/x = 1 only at x → 0** (radians). At x→∞, sin(x)/x → 0.

### Derivatives
- **Wrong chain rule**: d/dx[sin(x²)] = cos(x²) · 2x, NOT cos(x²)
- **Implicit differentiation**: d/dx[y²] = 2y · (dy/dx), NOT 2y
- **Parametric d²y/dx²**: = [d(dy/dx)/dt] / (dx/dt), NOT d²y/dt² / d²x/dt²
- **Logarithmic differentiation**: take ln|y| not ln(y) for potentially negative expressions

### Integration
- **Forgetting +C** for indefinite integrals — costs marks in JEE
- **∫1/x dx = ln|x| + C**: absolute value required; not just ln(x)
- **Integration by parts ILATE**: Logarithm before Algebraic, not after
- **Definite integral with odd function**: only equals 0 if limits are symmetric about 0 AND function is odd
- **King's property**: ∫ₐᵇ f(x)dx = ∫ₐᵇ f(a+b-x)dx — not ∫ₐᵇ f(b-x)dx (that's when a=0)

## Probability Mistakes

### Counting Errors
- **nPr vs nCr**: ordered selection = permutation (P); unordered = combination (C)
- **nCr = n!/[r!(n-r)!]**, not n!/(r! or just n!/r!)
- **Circular permutations**: (n-1)! NOT n! (one element fixed as reference)
- **With vs without replacement**: P changes between draws only for WITHOUT replacement

### Probability Calculation Errors
- **P(A|B) ≠ P(B|A)**: conditional probability is NOT symmetric
- **Mutually exclusive ≠ independent**: ME means P(A∩B) = 0; independent means P(A∩B) = P(A)P(B)
- **At least one**: use complement: P(at least one) = 1 - P(none) — don't sum all individual cases
- **Bayes' Theorem**: compute P(A) via total probability FIRST, then compute posterior

## Linear Algebra Mistakes

### Matrix Errors
- **AB ≠ BA**: matrix multiplication is NOT commutative (most common)
- **(AB)ᵀ = BᵀAᵀ**: order reverses for transpose of product (NOT AᵀBᵀ)
- **(AB)⁻¹ = B⁻¹A⁻¹**: order reverses for inverse of product
- **adj(AB) = adj(B)·adj(A)**: order reverses for adjoint of product

### Determinant Errors
- **det(kA) = kⁿ·det(A)** for n×n matrix — NOT k·det(A). This is the #1 JEE trap.
  Example: det(2A) for 3×3 = 8·det(A), NOT 2·det(A)
- **det(A+B) ≠ det(A) + det(B)**: determinant is NOT linear in the whole matrix
- **Row addition preserves det**: adding multiple of one row to another doesn't change det
- **Row swap changes det sign**: careful with sign when expanding by cofactors

## Domain and Range Errors

### Logarithms
- **Domain**: log(x) requires x > 0; log(x²) ≠ 2log(x) when x could be negative
- **log(x) + log(y) = log(xy)** only when both x > 0 AND y > 0
- **ln(1+x) series**: only valid for -1 < x ≤ 1

### Square Roots
- **√(x²) = |x|**, NOT x. (√4 = 2, not ±2)
- **Domain of √f(x)**: requires f(x) ≥ 0; always check
- **√a · √b = √(ab)** only when a, b ≥ 0

### Inverse Trig Functions
- **sin⁻¹(x)** has domain [-1,1] and range [-π/2, π/2]
- **cos⁻¹(x)** has domain [-1,1] and range [0, π]
- **sin(sin⁻¹(x)) = x** for x ∈ [-1,1]; but sin⁻¹(sin(x)) = x ONLY for x ∈ [-π/2, π/2]

## Miscellaneous JEE Traps

### Power and Exponent Errors
- **aᵐ·aⁿ = a^(m+n)** NOT a^(mn)
- **(aᵐ)ⁿ = a^(mn)** NOT a^(m+n)
- **(-1)^(2n) = 1**, **(-1)^(2n+1) = -1** for integer n

### Inequality Traps
- **Multiplying by negative**: x > 2 → -x < -2 (sign flips)
- **Squaring**: a > b does NOT imply a² > b² (fails when a < 0 or |a| < |b|)
- **AM-GM**: all terms must be non-negative; equality iff all equal

### Factorial and Binomial
- **0! = 1** (not 0)
- **nCr = 0 when r > n** (not undefined)
- **C(n, r) = C(n, n-r)**: using C(100, 97) = C(100, 3) saves computation

### General
- **Reading the question**: "exactly k", "at most k", "at least k" need different approaches
- **Integer/real solutions**: some problems specify integers — don't give fractional answers
- **Multiple correct answers (MCQ-2)**: check ALL options, not just the first that seems right
