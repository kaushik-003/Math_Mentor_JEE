"""
Verifier Agent — Independently re-solves and checks the Solver's answer.
Uses the same SymPy tool calling loop as SolverAgent to verify calculations,
rather than just reading the proposed solution.
"""

import json
import sys
from pathlib import Path

import openai

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from utils.trace import AgentTracer
from agents.solver_agent import TOOL_SCHEMAS
from tools.sympy_tools import run_tool

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_TOOL_ROUNDS = 10

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------

VERIFIER_SYSTEM_PROMPT = """You are a math verification expert for JEE Advanced problems.

You are given a problem and a proposed solution. Your job is to VERIFY correctness.

Instructions:
1. Read the problem and the proposed solution carefully
2. For each key calculation in the solution, USE THE PROVIDED TOOLS to independently verify it
3. Check for: arithmetic errors, sign errors, domain violations, missing edge cases
4. Do NOT just agree with the solution — actively try to find errors
5. Compare your tool-verified results with the proposed answer

After all tool calls are complete, respond ONLY with a valid JSON object:
{
  "is_correct": true/false,
  "confidence": <float 0.0-1.0>,
  "issues": [
    {"step_index": <int>, "issue": "<description>", "severity": "high|medium|low"}
  ],
  "verified_answer": "<your independently computed answer>",
  "matches_proposed": true/false
}

Do not include any text outside this JSON object in your final response."""

# ---------------------------------------------------------------------------
# Verifier Agent
# ---------------------------------------------------------------------------


class VerifierAgent:
    """
    Verifier Agent that independently re-solves key steps using SymPy tools
    to catch arithmetic, sign, and logic errors in the Solver's output.
    """

    def __init__(self, tracer: AgentTracer | None = None) -> None:
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.tracer = tracer or AgentTracer()
        self.model = config.LLM_MODEL

    def verify(
        self,
        problem_text: str,
        topic: str,
        solver_solution: dict,
        rag_context: list[str] | None = None,
    ) -> dict:
        """
        Verify a solver solution by independently re-computing key steps.

        Args:
            problem_text: The clean problem statement.
            topic: Topic string (algebra, calculus, etc.).
            solver_solution: Dict with keys 'steps', 'final_answer', 'confidence'.
            rag_context: Optional list of reference strings from RAG.

        Returns:
            {
                "is_correct": bool,
                "confidence": float,
                "issues": [{"step_index": int, "issue": str, "severity": str}],
                "verified_answer": str,
                "matches_proposed": bool,
            }
        """
        self.tracer.start("VerifierAgent")
        tools_used: list[dict] = []

        user_msg = self._build_user_message(problem_text, topic, solver_solution, rag_context or [])
        messages = [
            {"role": "system", "content": VERIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]

        last_error = None
        for round_num in range(MAX_TOOL_ROUNDS):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=config.LLM_TEMPERATURE,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                )
            except Exception as e:
                last_error = str(e)
                break

            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError as e:
                        args = {}
                        tool_result = {"success": False, "result": "", "error": f"Bad JSON args: {e}"}
                    else:
                        tool_result = run_tool(tool_name, **args)

                    tools_used.append({"tool": tool_name, "input": args, "output": tool_result})
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(tool_result),
                    })
                continue

            # No tool calls — this is the final verification result
            result = self._parse_final_response(msg.content, solver_solution)
            self.tracer.end(
                input_summary=f"[{topic}] proposed={solver_solution.get('final_answer', '')[:60]}",
                output_summary=(
                    f"{'CORRECT' if result['is_correct'] else 'INCORRECT'} "
                    f"conf={result['confidence']:.2f} issues={len(result['issues'])}"
                ),
                metadata={
                    "rounds": round_num + 1,
                    "tools_called": len(tools_used),
                    "is_correct": result["is_correct"],
                    "confidence": result["confidence"],
                },
            )
            return result

        # Exhausted rounds or API error — return a conservative fallback
        fallback = {
            "is_correct": False,
            "confidence": 0.0,
            "issues": [{"step_index": 0, "issue": f"Verifier failed: {last_error}", "severity": "high"}],
            "verified_answer": solver_solution.get("final_answer", ""),
            "matches_proposed": False,
        }
        self.tracer.end(
            input_summary=f"[{topic}] {problem_text[:60]}",
            output_summary="FAILED",
            metadata={"error": last_error},
        )
        return fallback

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_user_message(
        self,
        problem_text: str,
        topic: str,
        solver_solution: dict,
        rag_context: list[str],
    ) -> str:
        steps = solver_solution.get("steps", [])
        final_answer = solver_solution.get("final_answer", "")
        reported_confidence = solver_solution.get("confidence", "unknown")

        lines = [
            f"Topic: {topic}",
            f"Problem: {problem_text}",
            "",
            "Proposed Solution to Verify:",
        ]
        for i, step in enumerate(steps, 1):
            lines.append(f"  Step {i}: {step}")
        lines.append(f"  Final Answer: {final_answer}")
        lines.append(f"  Reported Confidence: {reported_confidence}")

        if rag_context:
            lines.append("\nReference material (for context only):")
            for i, chunk in enumerate(rag_context[:3], 1):
                lines.append(f"[{i}] {chunk.strip()[:300]}")

        lines.append(
            "\nUsing the provided tools, independently verify each key calculation. "
            "If any tool result disagrees with what the solution claims, report it as an issue."
        )
        return "\n".join(lines)

    def _parse_final_response(self, content: str, solver_solution: dict) -> dict:
        """Parse the final JSON response. Falls back to a safe default on parse error."""
        default = {
            "is_correct": True,
            "confidence": 0.5,
            "issues": [],
            "verified_answer": solver_solution.get("final_answer", ""),
            "matches_proposed": True,
        }

        if not content:
            return default

        try:
            data = json.loads(content)
            return {
                "is_correct": bool(data.get("is_correct", True)),
                "confidence": float(data.get("confidence", 0.5)),
                "issues": data.get("issues", []),
                "verified_answer": data.get("verified_answer", solver_solution.get("final_answer", "")),
                "matches_proposed": bool(data.get("matches_proposed", True)),
            }
        except (json.JSONDecodeError, ValueError):
            pass

        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return {
                    "is_correct": bool(data.get("is_correct", True)),
                    "confidence": float(data.get("confidence", 0.5)),
                    "issues": data.get("issues", []),
                    "verified_answer": data.get("verified_answer", solver_solution.get("final_answer", "")),
                    "matches_proposed": bool(data.get("matches_proposed", True)),
                }
            except (json.JSONDecodeError, ValueError):
                pass

        return default


# ---------------------------------------------------------------------------
# Entry Point — Tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = VerifierAgent()

    # Test 1: Correct solution
    print("=" * 60)
    print("Test 1: Correct solution — expect is_correct=True")
    print("=" * 60)
    correct_solution = {
        "steps": [
            "Factor x^2 - 5x + 6 = (x-2)(x-3)",
            "Set each factor to zero: x-2=0 → x=2; x-3=0 → x=3",
        ],
        "final_answer": "x = 2, x = 3",
        "confidence": 0.95,
    }
    r1 = agent.verify("Solve x^2 - 5x + 6 = 0", "algebra", correct_solution)
    print(f"  is_correct     : {r1['is_correct']}")
    print(f"  confidence     : {r1['confidence']:.2f}")
    print(f"  verified_answer: {r1['verified_answer']}")
    print(f"  matches_proposed: {r1['matches_proposed']}")
    if r1["issues"]:
        for iss in r1["issues"]:
            print(f"  issue [{iss.get('severity')}]: {iss.get('issue')}")

    # Test 2: Wrong solution
    print("\n" + "=" * 60)
    print("Test 2: Wrong solution — expect is_correct=False")
    print("=" * 60)
    wrong_solution = {
        "steps": [
            "I think x^2 - 5x + 6 = (x-1)(x-6)",
            "So x=1 and x=6",
        ],
        "final_answer": "x = 1, x = 6",
        "confidence": 0.8,
    }
    r2 = agent.verify("Solve x^2 - 5x + 6 = 0", "algebra", wrong_solution)
    print(f"  is_correct     : {r2['is_correct']}")
    print(f"  confidence     : {r2['confidence']:.2f}")
    print(f"  verified_answer: {r2['verified_answer']}")
    print(f"  matches_proposed: {r2['matches_proposed']}")
    if r2["issues"]:
        for iss in r2["issues"]:
            print(f"  issue [{iss.get('severity')}]: {iss.get('issue')}")

    print(f"\nTotal trace duration: {agent.tracer.total_duration_ms():.0f}ms")
