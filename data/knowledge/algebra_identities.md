# Algebra Identities

## Core Algebraic Identities

### Square and Cube Expansions
- (a + b)² = a² + 2ab + b²
- (a - b)² = a² - 2ab + b²
- (a + b)³ = a³ + 3a²b + 3ab² + b³
- (a - b)³ = a³ - 3a²b + 3ab² - b³
- a² - b² = (a + b)(a - b)
- a³ + b³ = (a + b)(a² - ab + b²)
- a³ - b³ = (a - b)(a² + ab + b²)
- a³ + b³ + c³ - 3abc = (a + b + c)(a² + b² + c² - ab - bc - ca)

### Symmetric Functions
If a + b = s and ab = p, then:
- a² + b² = s² - 2p
- a³ + b³ = s³ - 3sp = s(s² - 3p)
- a⁴ + b⁴ = (a² + b²)² - 2(ab)² = (s² - 2p)² - 2p²
- (a - b)² = s² - 4p  →  |a - b| = √(s² - 4p)

## Advanced Identities

### Newton's Power Sum Identities
Let pₙ = aⁿ + bⁿ (power sums with e₁ = a+b, e₂ = ab):
- p₁ = e₁
- p₂ = e₁p₁ - 2e₂ = e₁² - 2e₂
- p₃ = e₁p₂ - e₂p₁ = e₁³ - 3e₁e₂
- p₄ = e₁p₃ - e₂p₂

For three variables (a + b + c = e₁, ab + bc + ca = e₂, abc = e₃):
- a² + b² + c² = e₁² - 2e₂
- a³ + b³ + c³ = e₁³ - 3e₁e₂ + 3e₃ (or use a³+b³+c³ - 3abc = ... identity)

### Lagrange Identity
(a₁² + a₂²)(b₁² + b₂²) = (a₁b₁ + a₂b₂)² + (a₁b₂ - a₂b₁)²

### Sophie Germain Identity
a⁴ + 4b⁴ = (a² + 2b² + 2ab)(a² + 2b² - 2ab)

## Factoring Techniques

### Key Substitutions for Factoring
- If expression symmetric in a, b: try a + b = s, ab = p
- If a³ + b³ + c³ - 3abc appears: always factor as (a+b+c)(...)
- For cyclic expressions: check if a = b, b = c, or a = -b is a root

### Sum/Difference of nth Powers
- aⁿ - bⁿ is divisible by (a - b) for all n ≥ 1
- aⁿ - bⁿ is divisible by (a + b) for all even n
- aⁿ + bⁿ is divisible by (a + b) for all odd n

## Worked Examples

### Example 1 (Standard): Factor a³ + b³ + c³ - 3abc
Use identity: a³ + b³ + c³ - 3abc = ½(a + b + c)[(a-b)² + (b-c)² + (c-a)²]
Note: If a + b + c = 0, then a³ + b³ + c³ = 3abc.

### Example 2 (Tricky): Find a⁴ + b⁴ given a + b = 3, ab = 1
- a² + b² = (a+b)² - 2ab = 9 - 2 = 7
- a⁴ + b⁴ = (a² + b²)² - 2(ab)² = 49 - 2 = **47**

## JEE Traps
- (a + b)² ≠ a² + b²  (forgetting the 2ab term)
- a³ + b³ ≠ (a + b)³  (forgetting cross terms)
- When a + b + c = 0: use a³ + b³ + c³ = 3abc immediately — don't expand
- Sophie Germain: a⁴ + 4b⁴ factors nicely — don't leave as is

## Edge Cases
- a³ + b³ + c³ - 3abc = 0 does NOT mean a = b = c; it means a + b + c = 0 OR a = b = c
- The identity (a-b)² ≥ 0 → a² + b² ≥ 2ab is the basis for AM-GM
