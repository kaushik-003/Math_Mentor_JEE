"""
Router Agent — Topic Classifier for Math Problems.

Calls GPT-4o to classify a problem into one of the supported topics
(algebra, probability, calculus, linear_algebra) and identify a subtopic.
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

ROUTER_SYSTEM_PROMPT = """You are a math topic classifier for JEE Advanced problems.

Your task: Classify the given problem into EXACTLY ONE of these topics:
- algebra
- probability
- calculus
- linear_algebra

Also identify a specific subtopic within that domain.

Instructions:
1. Read the problem carefully.
2. Identify key mathematical concepts (equations, derivatives, probability, matrices, etc.).
3. Choose the MOST relevant primary topic from the four options above.
4. Identify the subtopic (e.g. "quadratic equations", "binomial distribution", "limits", "determinants").
5. Provide brief reasoning for your classification.

Output format — JSON only, no other text:
{
  "topic": "<one of: algebra, probability, calculus, linear_algebra>",
  "subtopic": "<specific subtopic, e.g. 'quadratic equations', 'derivatives', 'combinatorics'>",
  "reasoning": "<1-2 sentences explaining your classification>"
}

Examples:
- "Solve x² - 5x + 6 = 0" → topic: "algebra", subtopic: "quadratic equations"
- "Find d/dx[x³ sin(x)]" → topic: "calculus", subtopic: "derivatives"
- "Two balls drawn without replacement from a bag of 5..." → topic: "probability", subtopic: "combinatorics"
- "Find the determinant of [[1,2],[3,4]]" → topic: "linear_algebra", subtopic: "determinants"
- "Sum of first 10 terms of AP with a=3, d=2" → topic: "algebra", subtopic: "sequences and series"
- "Evaluate lim(x→0) sin(x)/x" → topic: "calculus", subtopic: "limits"
"""

# ---------------------------------------------------------------------------
# Router Agent
# ---------------------------------------------------------------------------

class RouterAgent:
    """
    Classifies a math problem into one of the supported topics using GPT-4o.
    Returns a dict with topic, subtopic, and reasoning.
    """

    def __init__(self, tracer: AgentTracer | None = None) -> None:
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.tracer = tracer or AgentTracer()
        self.model = config.LLM_MODEL

    def classify(self, problem_text: str) -> dict:
        """
        Classify a math problem into a topic.

        Args:
            problem_text: The problem statement as a plain string.

        Returns:
            {
                "topic": "algebra" | "probability" | "calculus" | "linear_algebra" | None,
                "subtopic": str,
                "reasoning": str,
            }
            On failure, topic is None and subtopic is "unknown".
        """
        self.tracer.start("RouterAgent")
        fallback = {"topic": None, "subtopic": "unknown", "reasoning": "Classification failed."}

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.0,  # Deterministic classification
                messages=[
                    {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Problem:\n{problem_text}"},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or ""
            result = json.loads(content)

            topic = result.get("topic", "").strip().lower()
            subtopic = result.get("subtopic", "unknown").strip()
            reasoning = result.get("reasoning", "").strip()

            # Validate topic is one of the supported options
            if topic not in config.SUPPORTED_TOPICS:
                print(
                    f"[Router] Unexpected topic '{topic}', defaulting to None. "
                    f"Supported: {config.SUPPORTED_TOPICS}"
                )
                topic = None

            classification = {
                "topic": topic,
                "subtopic": subtopic,
                "reasoning": reasoning,
            }

            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary=f"topic={topic}, subtopic={subtopic}",
                metadata=classification,
            )
            return classification

        except json.JSONDecodeError as e:
            print(f"[Router] JSON parse error: {e}")
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED (JSON parse error)",
                metadata={"error": str(e)},
            )
            return fallback

        except openai.APIError as e:
            print(f"[Router] OpenAI API error: {e}")
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED (API error)",
                metadata={"error": str(e)},
            )
            return fallback

        except Exception as e:
            print(f"[Router] Unexpected error: {e}")
            self.tracer.end(
                input_summary=problem_text[:80],
                output_summary="FAILED",
                metadata={"error": str(e)},
            )
            return fallback


# ---------------------------------------------------------------------------
# Entry Point — Test with one problem per topic
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    TEST_PROBLEMS = [
        {
            "problem": "Find all real roots of x³ - 6x² + 11x - 6 = 0 using factorization.",
            "expected_topic": "algebra",
        },
        {
            "problem": (
                "A box contains 4 red, 3 blue, and 2 green balls. "
                "Three balls are drawn at random without replacement. "
                "What is the probability that all three are of different colors?"
            ),
            "expected_topic": "probability",
        },
        {
            "problem": (
                "Evaluate the integral ∫₀^π x·sin(x) dx using integration by parts."
            ),
            "expected_topic": "calculus",
        },
        {
            "problem": (
                "Find the values of k for which the system "
                "kx + y + z = 1, x + ky + z = 1, x + y + kz = 1 "
                "has no solution."
            ),
            "expected_topic": "linear_algebra",
        },
    ]

    agent = RouterAgent()

    print("=" * 60)
    print("Router Agent — Classification Test")
    print("=" * 60)

    for i, item in enumerate(TEST_PROBLEMS, 1):
        problem = item["problem"]
        expected = item["expected_topic"]

        print(f"\nProblem {i}:")
        print(f"  {problem[:100]}{'...' if len(problem) > 100 else ''}")

        result = agent.classify(problem)

        match = "OK" if result["topic"] == expected else "MISMATCH"
        print(f"  Topic    : {result['topic']}  [{match}] (expected: {expected})")
        print(f"  Subtopic : {result['subtopic']}")
        print(f"  Reasoning: {result['reasoning']}")

    print(f"\n{'=' * 60}")
    print("Router Agent Trace")
    print("=" * 60)
    for step in agent.tracer.get_steps():
        print(f"  Agent : {step.agent_name}")
        print(f"  Input : {step.input_summary}")
        print(f"  Output: {step.output_summary}")
        print(f"  Time  : {step.duration_ms:.1f}ms")
        print()
    print(f"Total duration: {agent.tracer.total_duration_ms():.1f}ms")
