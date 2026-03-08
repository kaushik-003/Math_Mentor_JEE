# Determinants

## Core Formulas

### 2×2 Determinant
|a b|
|c d|  = ad - bc

### 3×3 Determinant (Cofactor Expansion along Row 1)
|a b c|
|d e f| = a·(ei - fh) - b·(di - fg) + c·(dh - eg)
|g h i|

**Sarrus Rule** (for 3×3): Copy first two columns, sum downward diagonals minus upward.

### Cofactor Expansion
Along any row i: det(A) = Σⱼ aᵢⱼ · (-1)^(i+j) · Mᵢⱼ
Along any column j: det(A) = Σᵢ aᵢⱼ · (-1)^(i+j) · Mᵢⱼ
Where Mᵢⱼ = minor (det of matrix with row i, col j removed)

## Properties of Determinants

### Row/Column Operations
1. Swapping two rows (or columns): det changes sign
2. Multiplying a row by k: det is multiplied by k
3. Adding k times one row to another: det unchanged

### Key Properties
- det(Aᵀ) = det(A)
- det(AB) = det(A)·det(B)
- det(A⁻¹) = 1/det(A)
- **det(kA) = kⁿ·det(A)** for n×n matrix (NOT k·det(A))
- If two rows are identical: det = 0
- If a row is all zeros: det = 0
- det(I) = 1
- det is linear in each row (but NOT in the whole matrix)

### Differentiation of Determinants
d/dx |f₁(x) f₂(x)| = |f₁'(x) f₂'(x)| + |f₁(x) f₂(x)|
     |g₁(x) g₂(x)|   |g₁(x)  g₂(x)|   |g₁'(x) g₂'(x)|
Differentiate one row at a time, sum the results.

## Area and Geometry Applications

### Area of Triangle with Vertices (x₁,y₁), (x₂,y₂), (x₃,y₃)
Area = ½ |x₁(y₂-y₃) + x₂(y₃-y₁) + x₃(y₁-y₂)|
     = ½ |det [[x₁,y₁,1],[x₂,y₂,1],[x₃,y₃,1]]|

### Condition for Collinearity
Three points (x₁,y₁), (x₂,y₂), (x₃,y₃) are collinear iff:
|x₁ y₁ 1|
|x₂ y₂ 1| = 0
|x₃ y₃ 1|

## Cramer's Rule

For system Ax = b with n equations:
xᵢ = det(Aᵢ) / det(A)
where Aᵢ = A with column i replaced by b.

Valid ONLY when det(A) ≠ 0 (unique solution case).

## System of Homogeneous Equations
Ax = 0:
- det(A) ≠ 0: only trivial solution x = 0
- det(A) = 0: infinitely many non-trivial solutions exist

## Worked Examples

### Example 1 (Standard): Evaluate |2 1 3|
                                   |4 0 2|
                                   |1 3 5|
Expand along row 2 (has a zero):
= -4·|1 3| + 0 - 2·|2 1|
     |3 5|          |1 3|
= -4·(5-9) - 2·(6-1)
= -4·(-4) - 2·5 = 16 - 10 = **6**

### Example 2 (Tricky — det(kA)): If det(A) = 5 for 3×3 A, find det(2A)
det(2A) = 2³·det(A) = 8·5 = **40** (NOT 2·5 = 10)

### Example 3 (JEE Advanced — Homogeneous System with parameter)
x + y + z = 0, x + 2y + 3z = 0, x + 3y + kz = 0 has non-trivial solutions when?
det([[1,1,1],[1,2,3],[1,3,k]]) = 0
= 1(2k-9) - 1(k-3) + 1(3-2) = 2k-9-k+3+1 = k-5 = 0
**k = 5**

## JEE Traps
- det(kA) = kⁿ·det(A): most common JEE numerical trap (n = matrix size, not 1)
- Row expansion: cofactor sign is (-1)^(i+j), careful with the sign pattern
- Adding multiples of rows: does NOT change determinant (but multiplying does)
- Singular matrix: det = 0 ↔ no inverse ↔ rows/cols are linearly dependent
- Area formula: always take absolute value; the ½ factor is essential

## Edge Cases
- det(0) = 0 (zero matrix has determinant 0)
- det(I) = 1 for any size
- Triangular matrix: det = product of diagonal entries
- Block diagonal matrix: det = product of determinants of diagonal blocks
- If matrix has a row of zeros after row reduction: det = 0 (rows linearly dependent)
