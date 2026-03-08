# Bayes' Theorem

## Core Formula

### Bayes' Theorem
P(Bᵢ|A) = P(A|Bᵢ) · P(Bᵢ) / P(A)

Where P(A) = Σ P(A|Bⱼ) · P(Bⱼ)  (law of total probability)

- P(Bᵢ): **prior probability** (before observing A)
- P(A|Bᵢ): **likelihood** (how likely A is under Bᵢ)
- P(Bᵢ|A): **posterior probability** (after observing A)

### Full Form (Multiple Hypotheses)
If B₁, B₂, ..., Bₙ are mutually exclusive and exhaustive:
P(Bᵢ|A) = P(A|Bᵢ) · P(Bᵢ) / [Σⱼ P(A|Bⱼ) · P(Bⱼ)]

## Tree Diagram Approach

### Steps to Solve with Tree Diagrams
1. First branch: the hypothesis events (B₁, B₂, ...) with prior probabilities
2. Second branch: the observation A given each Bᵢ, with likelihoods P(A|Bᵢ)
3. Each path probability = P(Bᵢ) · P(A|Bᵢ)
4. P(A) = sum of all paths that lead to A
5. P(Bᵢ|A) = [path through Bᵢ] / [total paths through A]

## Worked Examples

### Example 1 (Standard — Two Urns)
Urn 1: 3 red, 2 blue. Urn 2: 1 red, 4 blue. A urn is chosen at random, then a ball drawn.
Given the ball is red, find P(it came from Urn 1).

- P(U₁) = P(U₂) = 1/2
- P(R|U₁) = 3/5, P(R|U₂) = 1/5
- P(R) = (1/2)(3/5) + (1/2)(1/5) = 3/10 + 1/10 = 4/10 = 2/5
- P(U₁|R) = [(1/2)(3/5)] / (2/5) = (3/10) / (2/5) = (3/10)·(5/2) = **3/4**

### Example 2 (Tricky — Multi-stage with 3 Hypotheses)
Factory has 3 machines producing 20%, 30%, 50% of output. Defect rates: 5%, 3%, 2%.
A defective item is found. P(came from machine 3)?

- P(M₁) = 0.2, P(M₂) = 0.3, P(M₃) = 0.5
- P(D|M₁) = 0.05, P(D|M₂) = 0.03, P(D|M₃) = 0.02
- P(D) = 0.2·0.05 + 0.3·0.03 + 0.5·0.02 = 0.010 + 0.009 + 0.010 = 0.029
- P(M₃|D) = (0.5·0.02) / 0.029 = 0.010/0.029 = **10/29 ≈ 0.345**

### Example 3 (JEE-style — Disease Testing)
Disease affects 1% of population. Test is 95% accurate (95% true positive, 5% false positive).
If a person tests positive, P(actually has disease)?

- P(D) = 0.01, P(healthy) = 0.99
- P(+|D) = 0.95, P(+|healthy) = 0.05 (false positive rate)
- P(+) = 0.01·0.95 + 0.99·0.05 = 0.0095 + 0.0495 = 0.059
- P(D|+) = 0.0095 / 0.059 = **95/590 ≈ 16.1%** (surprisingly low!)

This illustrates that even with a 95% accurate test, a positive result doesn't mean 95% likely disease.

## JEE Traps
- Confusing P(A|B) with P(B|A): the whole point of Bayes is to reverse the conditioning
- Forgetting to compute P(A) as total probability before dividing
- Using Bayes when events are independent (Bayes reduces to prior; don't over-complicate)
- Partial tree diagrams: always ensure the hypothesis branches are exhaustive (sum to 1)
- Multi-stage problems: draw the full tree, don't try to shortcut

## Edge Cases
- If all likelihoods P(A|Bᵢ) are equal, posterior = prior (observation gives no new info)
- If P(A) = 0, Bayes' theorem is undefined; this means A is impossible
- Bayes can be applied in sequence: posterior from one stage becomes prior for next
