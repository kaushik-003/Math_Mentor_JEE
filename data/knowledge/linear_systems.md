# Linear Systems

## Matrix Form of Linear System
System Ax = b  where A is m×n coefficient matrix, x is n×1 unknown vector, b is m×1 RHS.

**Augmented matrix:** [A | b] — used for Gaussian elimination.

## Consistency Conditions (Rank Method)

### Rouché-Capelli Theorem
Let r = rank(A), r* = rank([A|b]), n = number of unknowns.

| Condition | Solution |
|-----------|---------|
| r ≠ r* | Inconsistent (no solution) |
| r = r* = n | Unique solution |
| r = r* < n | Infinitely many solutions (n - r free parameters) |

### Computing Rank
Row-reduce the matrix. Rank = number of non-zero rows after reduction.

## Homogeneous Systems (Ax = 0)

For homogeneous systems, b = 0, so [A|0] always has consistent augmented matrix (r = r*).
- det(A) ≠ 0 (A is invertible): **only trivial solution x = 0**
- det(A) = 0 (A is singular): **infinitely many non-trivial solutions**

Number of free parameters = n - rank(A)

## Gaussian Elimination

### Steps
1. Write augmented matrix [A|b]
2. Use row operations to get upper triangular (row echelon form):
   - Swap rows to bring largest pivot to top (partial pivoting)
   - Eliminate below each pivot
3. Back-substitute from bottom row upward

### Row Echelon Form
- Leading entry of each row is to the right of the leading entry in row above
- All zero rows at the bottom

### Reduced Row Echelon Form (RREF)
- Each leading entry = 1
- Each leading entry is the only non-zero in its column

## Cramer's Rule
For Ax = b with n equations and n unknowns, det(A) ≠ 0:
xᵢ = det(Aᵢ) / det(A)
where Aᵢ = A with the i-th column replaced by b.

Useful for small systems (2×2, 3×3). Not efficient for large systems.

## Parameter-Based Systems (JEE Type)

### Strategy for "Find k such that system has solutions"
1. Write augmented matrix [A(k)|b(k)]
2. Row-reduce keeping k symbolic
3. For NO solution: rank(A) ≠ rank([A|b])
4. For UNIQUE solution: rank(A) = rank([A|b]) = n
5. For INFINITE solutions: rank(A) = rank([A|b]) < n

**Common JEE pattern:** Find k for which system is inconsistent.

## Worked Examples

### Example 1 (Standard): 2x + y = 5, x + 3y = 10
Matrix form: [[2,1],[1,3]] · [x,y]ᵀ = [5,10]ᵀ
det(A) = 6-1 = 5 ≠ 0, so unique solution exists.
Cramer's: x = |5 1|/5 = (15-10)/5 = 1; y = |2 5|/5 = (20-5)/5 = 3
           |10 3|           |1 10|
**x = 1, y = 3**

### Example 2 (Parameter): Find k for which system is consistent
x + y + z = 1
x + 2y + 3z = k
x + 4y + 9z = k²

Augmented matrix [A|b], row reduce:
R2 = R2 - R1: [0, 1, 2 | k-1]
R3 = R3 - R1: [0, 3, 8 | k²-1]
R3 = R3 - 3R2: [0, 0, 2 | k²-3k+2] = [0, 0, 2 | (k-1)(k-2)]

For unique solution: (k-1)(k-2) can be anything, rank = 3.
For infinite solutions: need [0,0,2|(k-1)(k-2)] to imply 0 = 0, but 2 ≠ 0, so 2z = (k-1)(k-2) is always a valid equation.
Actually this system always has a unique solution when det(A) ≠ 0. det(A) = 2 ≠ 0 always.
**System always has unique solution** for all real k.

### Example 3 (JEE Advanced — Homogeneous): Non-trivial solutions
kx - y + z = 0, x - ky + z = 0, x - y + kz = 0
det = 0: |k  -1  1|
         |1  -k  1| = k((-k)(k)-1) + 1(k-1) + 1(-1+k)
         |1  -1  k|
= k(-k²-1) + (k-1) + (k-1) = -k³ - k + 2k - 2 = -k³ + k - 2

Wait: let's expand properly along row 1:
= k[(−k)(k) − (1)(−1)] − (−1)[(1)(k) − (1)(1)] + 1[(1)(−1) − (−k)(1)]
= k[−k² + 1] + 1[k − 1] + 1[−1 + k]
= −k³ + k + k − 1 − 1 + k = −k³ + 3k − 2

Set = 0: k³ - 3k + 2 = 0 → (k-1)²(k+2) = 0 → **k = 1 or k = -2**

## JEE Traps
- Cramer's rule requires det(A) ≠ 0; don't apply when system is singular
- rank([A|b]) can be higher than rank(A) if b is NOT in column space of A
- Homogeneous systems are always consistent (b=0 trivially works); question is uniqueness
- When eliminating, multiply/divide rows by constants — keep track!
- "Infinite solutions" means n - rank free parameters; the solution set is an affine subspace

## Edge Cases
- n = 1, 1 equation: unique if a ≠ 0; inconsistent if a = 0, b ≠ 0; infinite if a = b = 0
- Over-determined (more equations than unknowns): typically inconsistent; solution exists only by coincidence
- Under-determined (fewer equations than unknowns): never unique solution (always ≥ 1 free param if consistent)
