# Probability Distributions

## Binomial Distribution

### Formula
X ~ B(n, p): n independent trials, p = P(success) per trial
P(X = k) = C(n, k) · pᵏ · (1-p)^(n-k)  for k = 0, 1, ..., n

Let q = 1 - p:
- **Mean:** E(X) = np
- **Variance:** Var(X) = npq
- **Standard Deviation:** σ = √(npq)

### Cumulative Probabilities
P(X ≤ k) = Σ C(n,j) pʲ qⁿ⁻ʲ  for j = 0 to k
P(X ≥ k) = 1 - P(X ≤ k-1)

### Mode of Binomial Distribution
- If (n+1)p is an integer: modes at (n+1)p and (n+1)p - 1 (bimodal)
- Otherwise: mode = ⌊(n+1)p⌋

## Expected Value and Variance

### Discrete Random Variable
E(X) = Σ xᵢ · P(X = xᵢ)
Var(X) = E(X²) - [E(X)]²  =  Σ xᵢ² · P(X = xᵢ) - μ²

### Key Properties
- E(aX + b) = aE(X) + b
- Var(aX + b) = a²·Var(X)
- For independent X, Y: E(XY) = E(X)·E(Y)
- For independent X, Y: Var(X + Y) = Var(X) + Var(Y)

## Geometric Distribution
X = number of trials until first success; P(success) = p
P(X = k) = q^(k-1) · p  for k = 1, 2, 3, ...
- E(X) = 1/p
- Var(X) = q/p²
- Memoryless property: P(X > m + n | X > m) = P(X > n)

## Poisson Distribution (Approximation to Binomial)
When n is large and p is small, B(n, p) ≈ Poisson(λ = np):
P(X = k) = e^(-λ) · λᵏ / k!
- E(X) = λ,  Var(X) = λ  (mean = variance)

Use when: n ≥ 100, p ≤ 0.01 (rule of thumb)

## Conditional Expectation
E(X|A) = Σ xᵢ · P(X = xᵢ | A)
Law of total expectation: E(X) = Σ E(X|Bᵢ) · P(Bᵢ)

## Worked Examples

### Example 1 (Standard): Binomial — Coin flips
Fair coin tossed 10 times. P(exactly 4 heads)?
X ~ B(10, 1/2)
P(X = 4) = C(10, 4) · (1/2)⁴ · (1/2)⁶ = 210/1024 = **105/512**

### Example 2 (Tricky — Mean/Variance): Dice problem
A fair die is rolled n times. X = number of 6's.
E(X) = n/6, Var(X) = n · (1/6) · (5/6) = 5n/36

For the variance to equal the mean: 5n/36 = n/6 → 5/36 = 1/6, which is never true.
(Mean = variance only for Poisson, not binomial in general.)

### Example 3 (JEE-style): Distribution-based problem
P(X = 1) = P(X = 2). X ~ B(n, 1/3). Find n.
P(X=1) = C(n,1)(1/3)(2/3)^(n-1)
P(X=2) = C(n,2)(1/3)²(2/3)^(n-2)
Set equal: n(2/3)^(n-1) = [n(n-1)/2](1/9)(2/3)^(n-2)
2/3 = (n-1)/18 → n - 1 = 12 → **n = 13**

## JEE Traps
- Binomial: n must be a fixed, known integer (not variable)
- P(X = k) requires C(n,k), not C(n-1,k) — use exactly n choose k
- Variance ≠ Standard deviation: Var = σ², SD = σ = √(Var)
- E(X²) ≠ [E(X)]²: must compute separately
- For "at least k" problems: P(X ≥ k) = 1 - P(X ≤ k-1), not 1 - P(X = k)
- Poisson approximation: only valid for large n, small p; don't apply blindly

## Edge Cases
- B(1, p) is Bernoulli distribution: P(X=1) = p, P(X=0) = q
- B(n, 0): always 0 successes; B(n, 1): always n successes
- Geometric distribution: k starts at 1, not 0
- If λ = 0 in Poisson: P(X=0) = 1, all other probabilities = 0
