# Demo Files

This folder contains pre-tested demo inputs for showcasing Math Mentor.

## demo_questions.txt

Five questions designed to demonstrate different features:

1. **Text + Solve Mode** — Binomial probability (clean text input, full pipeline)
2. **Image + HITL #1** — Quadratic equation screenshot (OCR, confidence badge, input editing)
3. **Audio + Hint Mode** — Derivative problem (Whisper transcription, progressive hints)
4. **HITL #3 Trigger** — Linear system with parameter (low verifier confidence, manual review)
5. **Memory Reuse** — Rephrased version of question #1 (triggers "Similar problem found!")

## Usage

1. Clear memory before starting: use the **Clear Memory** button in the sidebar
2. Ensure the knowledge base is built: `uv run python -m rag.embedder`
3. Run questions in order — question #5 depends on #1 being solved first
