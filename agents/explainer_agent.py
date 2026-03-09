"""
Explainer / Tutor Agent — Rewrites the verified solution for a student.
Pure text generation — no tool calls. Formats the solution into four
clear educational sections suitable for a JEE aspirant.
"""

import json
import sys
from pathlib import Path

import openai

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from utils.trace import AgentTracer

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------

EXPLAINER_SYSTEM_PROMPT = """You are a friendly JEE Advanced math tutor explaining a solution to a student.

Rewrite the solution in a clear, educational format with these EXACT sections:

## Concept Used
What mathematical concept/theorem is being applied (1-2 sentences)

## Step-by-Step Solution
Numbered steps with clear explanations. For each step explain WHY, not just WHAT.
Use simple language. A 16-year-old JEE aspirant should understand.

## Common Mistake to Avoid
One specific mistake students often make on this type of problem.

## Practice Tip
One actionable tip for getting faster or more accurate at this type of problem.

Return JSON only:
{
  "explanation": "<full markdown formatted explanation with all 4 sections>",
  "concept": "<short concept name, e.g. 'Quadratic Factorisation'>",
  "difficulty": "easy|medium|hard"
}"""

HINT_SYSTEM_PROMPT = """You are a JEE Advanced math tutor helping a student learn to solve problems on their own.
Do NOT solve the problem. Do NOT give the final answer.

Instead, guide the student with:

## What Type of Problem Is This?
Identify the category and what concept is being tested (1-2 sentences)

## Key Formulas You'll Need
List the specific formulas or identities relevant to this problem (pull from the provided context)

## Approach — How to Think About It
Step-by-step STRATEGY (not solution). Tell them what to do at each step, but don't do it for them.
Example: "Step 1: Set up the equation by..." NOT "Step 1: x² - 5x + 6 = (x-2)(x-3)"

## Watch Out For
One specific trap or common mistake for this problem type

## Check Your Answer
How the student can verify their own answer (e.g., "Substitute your roots back into the original equation")

Return JSON only:
{
  "hint": "<full markdown with all 5 sections above>",
  "concept": "<short concept name>",
  "difficulty": "easy|medium|hard",
  "estimated_time": "<e.g. 2-3 minutes>"
}"""

# ---------------------------------------------------------------------------
# Explainer Agent
# ---------------------------------------------------------------------------


class ExplainerAgent:
    """
    Explainer Agent that rewrites a verified solution into a student-friendly
    tutorial with concept, steps, common mistakes, and a practice tip.
    """

    def __init__(self, tracer: AgentTracer | None = None) -> None:
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.tracer = tracer or AgentTracer()
        self.model = config.LLM_MODEL

    def explain(
        self,
        problem_text: str,
        topic: str,
        verified_solution: dict,
        rag_context: list[str] | None = None,
    ) -> dict:
        """
        Rewrite a verified solution into a student-friendly explanation.

        Args:
            problem_text: The clean problem statement.
            topic: Topic string (algebra, calculus, etc.).
            verified_solution: Dict with keys 'steps', 'final_answer', 'confidence'.
            rag_context: Optional RAG reference strings for additional context.

        Returns:
            {
                "explanation": str,   # full markdown with all 4 sections
                "concept": str,       # short concept name
                "difficulty": str,    # "easy" | "medium" | "hard"
            }
        """
        self.tracer.start("ExplainerAgent")
        fallback = {
            "explanation": self._fallback_explanation(verified_solution),
            "concept": topic.replace("_", " ").title(),
            "difficulty": "medium",
        }

        try:
            user_msg = self._build_user_message(problem_text, topic, verified_solution, rag_context or [])

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.4,  # Slightly higher for more natural explanations
                messages=[
                    {"role": "system", "content": EXPLAINER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            data = json.loads(content)

            result = {
                "explanation": data.get("explanation", fallback["explanation"]).strip(),
                "concept": data.get("concept", topic.replace("_", " ").title()).strip(),
                "difficulty": data.get("difficulty", "medium").strip().lower(),
            }

            # Normalise difficulty value
            if result["difficulty"] not in ("easy", "medium", "hard"):
                result["difficulty"] = "medium"

            self.tracer.end(
                input_summary=f"[{topic}] answer={verified_solution.get('final_answer', '')[:60]}",
                output_summary=f"concept={result['concept']} difficulty={result['difficulty']}",
                metadata={"concept": result["concept"], "difficulty": result["difficulty"]},
            )
            return result

        except json.JSONDecodeError as e:
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED (JSON error)",
                metadata={"error": str(e)},
            )
            return fallback

        except openai.APIError as e:
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED (API error)",
                metadata={"error": str(e)},
            )
            return fallback

        except Exception as e:
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED",
                metadata={"error": str(e)},
            )
            return fallback

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_user_message(
        self,
        problem_text: str,
        topic: str,
        verified_solution: dict,
        rag_context: list[str],
    ) -> str:
        lines = [
            f"Topic: {topic}",
            f"Problem: {problem_text}",
            "",
            "Verified Solution:",
        ]
        for i, step in enumerate(verified_solution.get("steps", []), 1):
            lines.append(f"  Step {i}: {step}")
        lines.append(f"  Final Answer: {verified_solution.get('final_answer', '')}")

        if rag_context:
            lines.append("\nAdditional reference context (use if helpful for the explanation):")
            for i, chunk in enumerate(rag_context[:2], 1):
                lines.append(f"[{i}] {chunk.strip()[:300]}")

        lines.append("\nRewrite this as a clear, educational explanation for a JEE student.")
        return "\n".join(lines)

    def _fallback_explanation(self, verified_solution: dict) -> str:
        """Generate a minimal markdown explanation when the LLM call fails."""
        lines = ["## Step-by-Step Solution"]
        for i, step in enumerate(verified_solution.get("steps", []), 1):
            lines.append(f"{i}. {step}")
        final = verified_solution.get("final_answer", "")
        if final:
            lines.append(f"\n**Final Answer:** {final}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Hint mode
    # ------------------------------------------------------------------

    def hint(
        self,
        problem_text: str,
        topic: str,
        rag_context: list[str] | None = None,
        extra_nudge: bool = False,
    ) -> dict:
        """
        Generate hints and guidance without revealing the solution.

        Args:
            problem_text: The clean problem statement.
            topic: Topic string (algebra, calculus, etc.).
            rag_context: Optional RAG reference strings for additional context.
            extra_nudge: If True, adds instruction for a more specific hint.

        Returns:
            {
                "hint": str,           # full markdown with 5 sections
                "concept": str,        # short concept name
                "difficulty": str,     # "easy" | "medium" | "hard"
                "estimated_time": str, # e.g. "2-3 minutes"
            }
        """
        self.tracer.start("HintAgent")
        fallback = {
            "hint": "Could not generate hints. Please try again.",
            "concept": topic.replace("_", " ").title(),
            "difficulty": "medium",
            "estimated_time": "unknown",
        }

        try:
            user_msg = self._build_hint_user_message(
                problem_text, topic, rag_context or [], extra_nudge,
            )

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.4,
                messages=[
                    {"role": "system", "content": HINT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            data = json.loads(content)

            result = {
                "hint": data.get("hint", fallback["hint"]).strip(),
                "concept": data.get("concept", fallback["concept"]).strip(),
                "difficulty": data.get("difficulty", "medium").strip().lower(),
                "estimated_time": data.get("estimated_time", "unknown").strip(),
            }

            if result["difficulty"] not in ("easy", "medium", "hard"):
                result["difficulty"] = "medium"

            self.tracer.end(
                input_summary=f"[{topic}] {problem_text[:60]}",
                output_summary=f"concept={result['concept']} difficulty={result['difficulty']}",
                metadata={"concept": result["concept"], "difficulty": result["difficulty"]},
            )
            return result

        except json.JSONDecodeError as e:
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED (JSON error)",
                metadata={"error": str(e)},
            )
            return fallback

        except openai.APIError as e:
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED (API error)",
                metadata={"error": str(e)},
            )
            return fallback

        except Exception as e:
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED",
                metadata={"error": str(e)},
            )
            return fallback

    def _build_hint_user_message(
        self,
        problem_text: str,
        topic: str,
        rag_context: list[str],
        extra_nudge: bool,
    ) -> str:
        lines = [
            f"Topic: {topic}",
            f"Problem: {problem_text}",
        ]

        if rag_context:
            lines.append("\nReference context (use for formulas and concepts):")
            for i, chunk in enumerate(rag_context[:3], 1):
                lines.append(f"[{i}] {chunk.strip()[:300]}")

        if extra_nudge:
            lines.append(
                "\nThe student has already seen the initial hints. "
                "Give a more specific nudge toward the solution without revealing the answer."
            )

        lines.append("\nGuide the student without solving the problem.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry Point — Quick Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ExplainerAgent()

    verified = {
        "steps": [
            "Recognise the equation as a quadratic: x^2 - 5x + 6 = 0",
            "Find two numbers that multiply to 6 and add to -5: they are -2 and -3",
            "Factor: (x - 2)(x - 3) = 0",
            "Solve each factor: x = 2 or x = 3",
        ],
        "final_answer": "x = 2 or x = 3",
        "confidence": 0.98,
    }

    print("=" * 60)
    print("Explainer Agent — Test")
    print("=" * 60)

    result = agent.explain(
        problem_text="Solve x^2 - 5x + 6 = 0",
        topic="algebra",
        verified_solution=verified,
    )

    print(f"Concept   : {result['concept']}")
    print(f"Difficulty: {result['difficulty']}")
    print("\nExplanation:")
    print(result["explanation"])
    print(f"\nTrace duration: {agent.tracer.total_duration_ms():.0f}ms")
