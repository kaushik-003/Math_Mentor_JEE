"""
Parser Agent — Cleans and structures raw math problem input.

Handles OCR artifacts, ASR transcription noise, and ambiguous phrasing.
Follows the same pattern as RouterAgent.
"""

import json
import sys
from pathlib import Path

import openai

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from utils.trace import AgentTracer

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

PARSER_SYSTEM_PROMPT = """You are a math problem parser for JEE Advanced preparation.

Your task: Take raw input text (which may be messy from OCR or speech recognition) and convert it into a clean, structured math problem.

Instructions:
1. Fix OCR/ASR artifacts (misread symbols, spacing issues, garbled words)
2. Identify the core mathematical question
3. Extract variables, constraints, and what is being asked
4. Determine if the problem is clear enough to solve
5. If anything is ambiguous or missing, set needs_clarification to true

Return JSON only:
{
  "problem_text": "clean, well-formatted math problem statement",
  "topic": "best guess: algebra|probability|calculus|linear_algebra",
  "variables": ["x", "y"],
  "constraints": ["x > 0", "n is positive integer"],
  "what_to_find": "what the problem is asking for",
  "needs_clarification": false,
  "clarification_questions": [],
  "cleaned_from_original": true
}"""

# ---------------------------------------------------------------------------
# Parser Agent
# ---------------------------------------------------------------------------


class ParserAgent:
    """
    Cleans raw input text and returns a structured problem dict.
    Accepts an optional shared AgentTracer for multi-agent pipelines.
    """

    def __init__(self, tracer: AgentTracer | None = None) -> None:
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.tracer = tracer or AgentTracer()

    def parse(self, raw_text: str) -> dict:
        """
        Parse raw text into a structured math problem.

        Args:
            raw_text: Unprocessed input from typing, OCR, or ASR.

        Returns:
            {
                "problem_text": str,
                "topic": str | None,
                "variables": list[str],
                "constraints": list[str],
                "what_to_find": str,
                "needs_clarification": bool,
                "clarification_questions": list[str],
                "cleaned_from_original": bool,
            }
        """
        self.tracer.start("ParserAgent")

        fallback = {
            "problem_text": raw_text,
            "topic": None,
            "variables": [],
            "constraints": [],
            "what_to_find": "",
            "needs_clarification": True,
            "clarification_questions": ["Could you please clarify the problem statement?"],
            "cleaned_from_original": False,
        }

        try:
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": PARSER_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Raw input:\n{raw_text}"},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)

            topic = result.get("topic", "").strip().lower()
            if topic not in config.SUPPORTED_TOPICS:
                topic = None

            parsed = {
                "problem_text": result.get("problem_text", raw_text).strip(),
                "topic": topic,
                "variables": result.get("variables", []),
                "constraints": result.get("constraints", []),
                "what_to_find": result.get("what_to_find", ""),
                "needs_clarification": bool(result.get("needs_clarification", False)),
                "clarification_questions": result.get("clarification_questions", []),
                "cleaned_from_original": bool(result.get("cleaned_from_original", False)),
            }

            self.tracer.end(
                input_summary=raw_text[:80],
                output_summary=parsed["problem_text"][:80],
                metadata={
                    "topic": topic,
                    "needs_clarification": parsed["needs_clarification"],
                    "cleaned": parsed["cleaned_from_original"],
                },
            )
            return parsed

        except json.JSONDecodeError as e:
            self.tracer.end(
                input_summary=raw_text[:80],
                output_summary="FAILED (JSON parse error)",
                metadata={"error": str(e)},
            )
            return fallback

        except openai.APIError as e:
            self.tracer.end(
                input_summary=raw_text[:80],
                output_summary="FAILED (API error)",
                metadata={"error": str(e)},
            )
            return fallback

        except Exception as e:
            self.tracer.end(
                input_summary=raw_text[:80],
                output_summary="FAILED",
                metadata={"error": str(e)},
            )
            return fallback


# ---------------------------------------------------------------------------
# Entry Point — Quick smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    TEST_CASES = [
        {
            "label": "Clean text",
            "input": "Solve x^2 - 5x + 6 = 0",
        },
        {
            "label": "Messy OCR",
            "input": "Fmd the denvatrve of x3 sin(x) wrth respect to x",
        },
        {
            "label": "Speech text",
            "input": "what is the probability of getting exactly 3 heads in 5 coin tosses",
        },
    ]

    agent = ParserAgent()

    print("=" * 60)
    print("Parser Agent — Smoke Test")
    print("=" * 60)

    for case in TEST_CASES:
        print(f"\n[{case['label']}]")
        print(f"  Input : {case['input']}")
        result = agent.parse(case["input"])
        print(f"  Parsed: {result['problem_text']}")
        print(f"  Topic : {result['topic']}")
        print(f"  Find  : {result['what_to_find']}")
        print(f"  Needs clarification: {result['needs_clarification']}")
        if result["clarification_questions"]:
            print(f"  Questions: {result['clarification_questions']}")
        if result["cleaned_from_original"]:
            print("  (text was cleaned from original)")

    print(f"\n{'=' * 60}")
    print("Trace")
    print("=" * 60)
    for step in agent.tracer.get_steps():
        print(f"  {step.agent_name} — {step.duration_ms:.0f}ms")
        print(f"    In : {step.input_summary}")
        print(f"    Out: {step.output_summary}")
        print(f"    Meta: {step.metadata}")
