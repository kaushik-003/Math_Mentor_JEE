# Evaluation Report

## Test Setup

| Parameter | Value |
|-----------|-------|
| Model | GPT-4o |
| Knowledge base | 18 files, 248 chunks |
| Embedding model | text-embedding-3-small |
| Verifier confidence threshold | 0.75 |
| Memory similarity threshold | 0.85 |
| Test date | 2026-03-10 |

---

## Test Results

| # | Question | Topic | Expected Answer | System Answer | Correct? | Confidence | Verified? | Notes |
|---|----------|-------|----------------|---------------|----------|------------|-----------|-------|
| 1 | Solve x² - 7x + 12 = 0 | Algebra | x = 3, x = 4 | | | | | |
| 2 | If roots of 2x² + kx + 3 = 0 are equal, find k | Algebra | k = ±2√6 | | | | | |
| 3 | Sum of 1 + 3 + 5 + ... + 99 | Algebra | 2500 | | | | | |
| 4 | P(both red) from 5 red, 3 blue, draw 2 without replacement | Probability | 5/14 | | | | | |
| 5 | P(X = 2) for B(6, 1/3) | Probability | 80/243 | | | | | |
| 6 | P(sum ≥ 10) for two fair dice | Probability | 1/6 | | | | | |
| 7 | d/dx [x³ · sin(x)] | Calculus | x²(x·cos(x) + 3·sin(x)) | | | | | |
| 8 | lim(x → 0) sin(3x)/x | Calculus | 3 | | | | | |
| 9 | Maximum value of f(x) = -x² + 4x + 5 | Calculus | 9 at x = 2 | | | | | |
| 10 | det([[2, 3], [1, 4]]) | Linear Algebra | 5 | | | | | |

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Accuracy | _/10 |
| Average confidence | |
| HITL #3 triggers | |
| Average solve time | |

---

## RAG Quality

| Aspect | Observation |
|--------|-------------|
| **Context relevance** | Were retrieved docs on-topic for each question? |
| **Faithfulness** | Did solutions follow from retrieved context? |
| **Chunk utilization** | How many of the top-5 retrieved chunks were actually relevant? |

---

## Memory Test

| Step | Details |
|------|---------|
| First solve | Run question #5: "P(X = 2) for B(6, 1/3)" |
| Second solve (rephrased) | "Find the probability of exactly 2 successes in 6 trials with p = 1/3" |
| Expected behavior | "Similar problem found!" message should appear |
| Result | |

---

## Hint Mode Test

| Step | Details |
|------|---------|
| Question | "Find the derivative of x³ · sin(x)" |
| Mode | Hint & Guide |
| Expected | 5 progressive hint sections, no answer revealed |
| "Show Full Solution" | Should trigger full solve pipeline |
| Result | |

---

## Multimodal Input Test

| Input Mode | Test | Expected | Result |
|-----------|------|----------|--------|
| **Image** | Screenshot of a handwritten quadratic equation | OCR extracts equation with confidence > 0.7 | |
| **Audio** | Record "Find the limit of sin 3x over x as x approaches zero" | Transcript correctly parsed with math symbols | |

---

## Known Limitations

- **Complex matrix arithmetic** — Cayley-Hamilton theorem, matrix inverse computation, and eigenvalue problems may hit SymPy tool limitations
- **Multi-part questions** — Questions with parts (a), (b), (c) are parsed as a single problem; the solver may miss sub-parts
- **Geometry/diagram-based problems** — No diagram understanding beyond OCR text extraction
- **Numerical approximations** — Some probability/combinatorics questions may return decimal approximations instead of exact fractions
- **Audio quality** — Whisper confidence is heuristic-based (audio length); noisy recordings may produce poor transcriptions
- **Single-turn only** — No conversational follow-up; each submission is independent (memory provides cross-session context, not within-session dialogue)
