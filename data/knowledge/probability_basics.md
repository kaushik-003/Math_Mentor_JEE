# Probability Basics

## Core Definitions

### Sample Space and Events
- Sample space S: set of all possible outcomes
- Event A: subset of S
- P(A) = |A|/|S| for equally likely outcomes (classical probability)
- P(A) ∈ [0, 1];  P(S) = 1;  P(∅) = 0

### Complement
P(A') = 1 - P(A)  where A' = complement of A

### Addition Rule
P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
For mutually exclusive events (A ∩ B = ∅): P(A ∪ B) = P(A) + P(B)

### Inclusion-Exclusion for 3 Events
P(A ∪ B ∪ C) = P(A) + P(B) + P(C) - P(A∩B) - P(B∩C) - P(A∩C) + P(A∩B∩C)

### Multiplication Rule
P(A ∩ B) = P(A) · P(B|A) = P(B) · P(A|B)
For independent events: P(A ∩ B) = P(A) · P(B)

## Conditional Probability
P(A|B) = P(A ∩ B) / P(B)  for P(B) > 0
- Read as: "probability of A given B has occurred"
- P(A|B) ≠ P(B|A) in general (common mistake!)

### Independence
A and B are independent iff:
- P(A ∩ B) = P(A) · P(B)
- Equivalently: P(A|B) = P(A) and P(B|A) = P(B)

Note: Mutually exclusive events with P(A), P(B) > 0 are NEVER independent.

## Advanced Techniques

### Derangements
Number of permutations of n objects where NO object appears in its original position:
D(n) = n! · Σ(-1)^k/k! for k = 0 to n = n! · (1 - 1/1! + 1/2! - 1/3! + ... + (-1)^n/n!)

Approximate: D(n) ≈ n!/e  for large n
- D(1) = 0, D(2) = 1, D(3) = 2, D(4) = 9

Probability that a random permutation is a derangement → 1/e ≈ 0.368

### Geometric Probability
P(A) = measure(A) / measure(S)  (length, area, or volume ratio)
Used when sample space is continuous.

Example: A point is chosen at random from [0, 1]. P(x² < x) = P(0 < x < 1) = 1.
Example: Two numbers x, y chosen from [0,1]. P(x + y < 1) = area of triangle = 1/2.

### Law of Total Probability
If B₁, B₂, ..., Bₙ partition S (mutually exclusive, exhaustive):
P(A) = Σ P(A|Bᵢ) · P(Bᵢ)  for i = 1 to n

## Worked Examples

### Example 1 (Standard): Drawing from a deck
A card is drawn from a 52-card deck. P(King or Heart)?
P(K) = 4/52, P(H) = 13/52, P(K∩H) = 1/52 (King of Hearts)
P(K ∪ H) = 4/52 + 13/52 - 1/52 = **16/52 = 4/13**

### Example 2 (Tricky — Inclusion-Exclusion): Birthday problem (no match)
P(all 23 people have different birthdays) = 365·364·...·343 / 365²³ ≈ 0.493
So P(at least two share birthday) ≈ 0.507 > 50%. Counterintuitive!

### Example 3 (Geometric): Bertrand paradox setup
Two numbers x, y chosen randomly from [0, 10]. P(x + y ≤ 10)?
Favorable area = triangle with vertices (0,0),(10,0),(0,10): area = 50.
Total area of sample space [0,10]×[0,10] = 100.
P = 50/100 = **1/2**

## JEE Traps
- P(A|B) ≠ P(B|A): don't confuse conditional probability direction
- "At least one" problems: use complement P(at least one A) = 1 - P(none)
- Independent vs mutually exclusive: two non-trivial mutually exclusive events are DEPENDENT
- Addition rule: always subtract P(A ∩ B) to avoid double-counting
- "Without replacement" affects subsequent probabilities; "with replacement" doesn't
- Inclusion-exclusion for 3 events: remember the +P(A∩B∩C) term at the end

## Edge Cases
- P(A) = 0 doesn't mean A is impossible (in continuous probability)
- If A ⊂ B, then P(A) ≤ P(B)
- P(A|B) is undefined when P(B) = 0
- "Equally likely" assumption must be verified, not assumed
