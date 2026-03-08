# Matrices

## Types of Matrices

| Type | Definition |
|------|-----------|
| Row matrix | 1 × n |
| Column matrix | m × 1 |
| Square matrix | m × m |
| Diagonal matrix | aᵢⱼ = 0 for i ≠ j |
| Identity matrix I | diagonal = 1, rest = 0 |
| Zero matrix 0 | all entries = 0 |
| Upper triangular | aᵢⱼ = 0 for i > j |
| Lower triangular | aᵢⱼ = 0 for i < j |
| Symmetric | A = Aᵀ |
| Skew-symmetric | A = -Aᵀ (diagonal = 0) |
| Orthogonal | AᵀA = I, i.e., A⁻¹ = Aᵀ |

## Matrix Operations

### Addition and Scalar Multiplication
(A + B)ᵢⱼ = Aᵢⱼ + Bᵢⱼ (same dimensions required)
(cA)ᵢⱼ = c·Aᵢⱼ

### Matrix Multiplication
(AB)ᵢⱼ = Σₖ Aᵢₖ·Bₖⱼ
- A is m×n, B is n×p → AB is m×p
- **NOT commutative: AB ≠ BA in general**
- Associative: (AB)C = A(BC)
- Distributive: A(B+C) = AB + AC

### Transpose
(Aᵀ)ᵢⱼ = Aⱼᵢ
Properties:
- (Aᵀ)ᵀ = A
- (AB)ᵀ = BᵀAᵀ  (ORDER REVERSES)
- (A + B)ᵀ = Aᵀ + Bᵀ
- (cA)ᵀ = c·Aᵀ

## Advanced Matrix Theory

### Adjoint (Adjugate) Matrix
adj(A): replace each element by its cofactor, then transpose.
For 2×2: adj([[a,b],[c,d]]) = [[d,-b],[-c,a]]

Properties of adjoint:
- A · adj(A) = adj(A) · A = det(A) · I
- adj(AB) = adj(B) · adj(A)  (ORDER REVERSES)
- adj(Aᵀ) = [adj(A)]ᵀ
- det(adj(A)) = det(A)^(n-1) for n×n matrix

### Matrix Inverse
A⁻¹ = adj(A) / det(A)  (exists iff det(A) ≠ 0)
- (AB)⁻¹ = B⁻¹A⁻¹  (ORDER REVERSES)
- (Aᵀ)⁻¹ = (A⁻¹)ᵀ
- det(A⁻¹) = 1/det(A)

### Cayley-Hamilton Theorem
Every square matrix satisfies its own characteristic equation.
If char. poly. of A is p(λ) = λⁿ + a_{n-1}λⁿ⁻¹ + ... + a₁λ + a₀, then:
p(A) = Aⁿ + a_{n-1}Aⁿ⁻¹ + ... + a₁A + a₀I = 0

Use: find A⁻¹, powers of A, without direct computation.

Example for 2×2: If char. poly. is λ² - (tr A)λ + det(A) = 0, then A² - (tr A)A + (det A)I = 0.
So A² = (tr A)A - (det A)I; also A⁻¹ = [A - (tr A)I]/(-det A).

### Special Matrix Classes
- **Idempotent:** A² = A  (eigenvalues are 0 or 1)
- **Involutory:** A² = I (A is its own inverse; eigenvalues ±1)
- **Nilpotent:** Aᵏ = 0 for some k (all eigenvalues = 0)
- **Orthogonal:** AᵀA = I = AAᵀ (columns/rows are orthonormal; det = ±1)

## Worked Examples

### Example 1 (Standard): Multiply A = [[1,2],[3,4]] by B = [[5,6],[7,8]]
AB[1,1] = 1·5 + 2·7 = 19; AB[1,2] = 1·6 + 2·8 = 22
AB[2,1] = 3·5 + 4·7 = 43; AB[2,2] = 3·6 + 4·8 = 50
**AB = [[19,22],[43,50]]**

### Example 2 (Cayley-Hamilton): Find A⁻¹ for A = [[2,1],[1,1]]
tr(A) = 3, det(A) = 2-1 = 1
Char poly: λ² - 3λ + 1 = 0
By Cayley-Hamilton: A² - 3A + I = 0 → A(A - 3I) = -I → A⁻¹ = -(A - 3I) = 3I - A
**A⁻¹ = [[1,-1],[-1,2]]** (verify: det = 2-1 = 1 = 1/det(A) ✓)

## JEE Traps
- (AB)ᵀ = BᵀAᵀ — order reverses, not (AB)ᵀ = AᵀBᵀ
- AB ≠ BA — never assume commutativity unless explicitly stated
- det(kA) = kⁿ det(A) for n×n, NOT k·det(A)
- adj(AB) = adj(B)·adj(A) — order reverses like inverse
- Orthogonal matrix: det = ±1, NOT necessarily +1

## Edge Cases
- If A is symmetric: A = Aᵀ, so eigenvalues are real
- For 2×2: adj(A) can be written by inspection (swap diagonal, negate off-diagonal)
- Null matrix has no inverse; any matrix times null = null
- A + (-A) = 0 (zero matrix, additive inverse)
