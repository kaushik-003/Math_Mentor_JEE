# Combinatorics

## Core Formulas

### Permutations
- nPr = n!/(n-r)! = n·(n-1)·...·(n-r+1)  (ordered, r from n distinct)
- Permutations of all n: n!
- With repetition: nʳ ways to choose r from n with repetition

### Combinations
- nCr = n!/[r!(n-r)!]  (unordered, r from n distinct)
- nC0 = nCn = 1
- nCr = nC(n-r)  (symmetry)
- nCr + nC(r-1) = (n+1)Cr  (Pascal's identity)

### Permutations with Repeated Elements
n objects with repetitions n₁, n₂, ..., nₖ: n!/(n₁!·n₂!·...·nₖ!) = multinomial coefficient

### Circular Permutations
- n distinct objects in a circle: (n-1)!
- n objects in a circle with clockwise ≠ anticlockwise: (n-1)!
- If necklace/bracelet (flipping gives same): (n-1)!/2

## Advanced Counting Techniques

### Stars and Bars
Number of non-negative integer solutions to x₁ + x₂ + ... + xₖ = n:
**C(n + k - 1, k - 1)**

Number of positive integer solutions (xᵢ ≥ 1) to same:
C(n - 1, k - 1)  [substitute yᵢ = xᵢ - 1]

Example: Ways to put 10 identical balls in 4 distinct boxes = C(13, 3) = 286

### Distributing Objects into Groups

**Identical objects, distinct boxes:** Stars and bars (as above)

**Distinct objects, distinct boxes (each box non-empty):**
Number of surjective functions = Σ(-1)^k · C(n,k) · (n-k)^m  (inclusion-exclusion)
Or use Stirling numbers of second kind: m! · S(n, m)

**Distinct objects, identical boxes:**
Number of partitions = Bell numbers or Stirling numbers

### Derangements
D(n) = n! · (1 - 1/1! + 1/2! - 1/3! + ... + (-1)^n/n!)
= Σ(-1)^k · n!/k! for k = 0 to n

Values: D(1)=0, D(2)=1, D(3)=2, D(4)=9, D(5)=44

Recurrence: D(n) = (n-1)[D(n-1) + D(n-2)] for n ≥ 2

### Multinomial Coefficients
Coefficient of x₁^a₁ · x₂^a₂ · ... · xₖ^aₖ in (x₁ + x₂ + ... + xₖ)^n
= n!/(a₁!·a₂!·...·aₖ!) where a₁ + a₂ + ... + aₖ = n

### Inclusion-Exclusion Principle
|A₁ ∪ A₂ ∪ ... ∪ Aₙ| = Σ|Aᵢ| - Σ|Aᵢ∩Aⱼ| + Σ|Aᵢ∩Aⱼ∩Aₖ| - ...

Number of integers from 1 to N divisible by at least one of a, b, c:
= ⌊N/a⌋ + ⌊N/b⌋ + ⌊N/c⌋ - ⌊N/lcm(a,b)⌋ - ⌊N/lcm(b,c)⌋ - ⌊N/lcm(a,c)⌋ + ⌊N/lcm(a,b,c)⌋

### Circular Permutations with Restrictions
Technique: Fix one person/element, arrange the rest.
For n people with specific constraint (e.g., 2 people must not be adjacent):
Total - (arrangements where they ARE adjacent) = (n-1)! - 2·(n-2)!

## Worked Examples

### Example 1 (Standard): 5 people in a row, A and B always together
Treat A+B as one unit → 4 units, 4! arrangements × 2 (A,B or B,A internal) = **48**

### Example 2 (Tricky — Stars & Bars): Distribute ₹20 among 3 people, each getting at least ₹3
Let xᵢ be amount to person i, xᵢ ≥ 3.
Substitute yᵢ = xᵢ - 3, yᵢ ≥ 0, y₁ + y₂ + y₃ = 20 - 9 = 11
Solutions: C(11 + 2, 2) = C(13, 2) = **78**

### Example 3 (JEE Advanced — Derangements): 5 letters in 5 envelopes, none in correct envelope
D(5) = 5!(1 - 1 + 1/2 - 1/6 + 1/24 - 1/120) = 120(44/120) = **44**

## JEE Traps
- nPr vs nCr: ORDER matters for P, doesn't for C. "Arrangement" → P; "selection" → C
- Circular permutations: (n-1)! NOT n! (fixing one reference point)
- Stars and bars: non-negative vs positive solutions — different formula
- Derangements: D(n) ≠ n! - n — there are MANY more non-derangement-permutations
- "At least" problems: usually easier with complement method
- Overcounting: divide by symmetry when identical objects are involved

## Edge Cases
- 0! = 1 (important for formulas with 0 in factorial)
- nC0 = 1 (one way to choose nothing)
- Derangement D(0) = 1 (empty permutation is a derangement vacuously)
- Circular permutations of identical objects = 1 (all arrangements look the same)
