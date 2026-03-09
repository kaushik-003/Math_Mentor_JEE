"""
Refiner Agent — Corrects solutions when the Verifier finds issues.
Uses the same SymPy tool calling loop as SolverAgent to re-solve correctly.
Runs at most config.MAX_REFINER_ITERATIONS times (currently 1).
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

REFINER_SYSTEM_PROMPT = """You are a math solution corrector for JEE Advanced problems.

A previous solution attempt had errors. Your job is to fix them.

Instructions:
1. Understand what went wrong based on the issues provided
2. Re-solve the problem correctly using the provided tools
3. Fix the specific issues identified — do not repeat the same mistakes
4. Return a complete corrected solution

After all tool calls are complete, respond ONLY with a valid JSON object:
{
  "steps": ["step1", "step2", ...],
  "final_answer": "<corrected answer>",
  "tools_used": [],
  "confidence": <float 0.0-1.0>,
  "corrections_made": ["description of what was fixed"]
}

Do not include any text outside this JSON object in your final response."""

# ---------------------------------------------------------------------------
# Refiner Agent
# ---------------------------------------------------------------------------


class RefinerAgent:
    """
    Refiner Agent that fixes solver output when the Verifier flags issues.
    Re-solves using SymPy tools with knowledge of what went wrong.
    """

    def __init__(self, tracer: AgentTracer | None = None) -> None:
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.tracer = tracer or AgentTracer()
        self.model = config.LLM_MODEL

    def refine(
        self,
        problem_text: str,
        topic: str,
        failed_solution: dict,
        verifier_issues: list[dict],
        rag_context: list[str] | None = None,
    ) -> dict:
        """
        Produce a corrected solution given the original failed attempt and
        the issues the Verifier identified.

        Args:
            problem_text: The clean problem statement.
            topic: Topic string.
            failed_solution: Original solver output dict.
            verifier_issues: List of issue dicts from VerifierAgent.verify().
            rag_context: Optional RAG reference strings.

        Returns:
            {
                "steps": [...],
                "final_answer": str,
                "tools_used": [...],
                "confidence": float,
                "corrections_made": [...],
            }
        """
        self.tracer.start("RefinerAgent")
        tools_used: list[dict] = []

        user_msg = self._build_user_message(
            problem_text, topic, failed_solution, verifier_issues, rag_context or []
        )
        messages = [
            {"role": "system", "content": REFINER_SYSTEM_PROMPT},
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

            # Final corrected solution
            result = self._parse_final_response(msg.content, tools_used)
            self.tracer.end(
                input_summary=f"[{topic}] issues={len(verifier_issues)} failed_ans={failed_solution.get('final_answer', '')[:40]}",
                output_summary=f"refined_ans={result.get('final_answer', '')[:60]} conf={result.get('confidence', 0):.2f}",
                metadata={
                    "rounds": round_num + 1,
                    "tools_called": len(tools_used),
                    "corrections": len(result.get("corrections_made", [])),
                },
            )
            return result

        # Exhausted rounds or API error — return the original failed solution with an error note
        error_result = {
            "steps": failed_solution.get("steps", []),
            "final_answer": failed_solution.get("final_answer", ""),
            "tools_used": tools_used,
            "confidence": 0.0,
            "corrections_made": [f"Refiner failed after {MAX_TOOL_ROUNDS} rounds. Last error: {last_error}"],
        }
        self.tracer.end(
            input_summary=f"[{topic}] {problem_text[:60]}",
            output_summary="FAILED",
            metadata={"error": last_error},
        )
        return error_result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_user_message(
        self,
        problem_text: str,
        topic: str,
        failed_solution: dict,
        verifier_issues: list[dict],
        rag_context: list[str],
    ) -> str:
        lines = [
            f"Topic: {topic}",
            f"Problem: {problem_text}",
            "",
            "Failed Solution (DO NOT REPEAT THESE MISTAKES):",
        ]
        for i, step in enumerate(failed_solution.get("steps", []), 1):
            lines.append(f"  Step {i}: {step}")
        lines.append(f"  Final Answer: {failed_solution.get('final_answer', '')}")

        if verifier_issues:
            lines.append("")
            lines.append("Issues Found by Verifier:")
            for iss in verifier_issues:
                severity = iss.get("severity", "?")
                issue_text = iss.get("issue", "")
                step_idx = iss.get("step_index", "?")
                lines.append(f"  [{severity.upper()}] Step {step_idx}: {issue_text}")

        if rag_context:
            lines.append("\nReference material:")
            for i, chunk in enumerate(rag_context[:3], 1):
                lines.append(f"[{i}] {chunk.strip()[:300]}")

        lines.append(
            "\nRe-solve the problem correctly using the tools. "
            "Fix every issue listed above. Return a complete corrected solution."
        )
        return "\n".join(lines)

    def _parse_final_response(self, content: str, tools_used: list[dict]) -> dict:
        """Parse the final JSON response. Falls back gracefully on parse errors."""
        default = {
            "steps": [],
            "final_answer": "",
            "tools_used": tools_used,
            "confidence": 0.3,
            "corrections_made": [],
        }

        if not content:
            return default

        try:
            data = json.loads(content)
            return {
                "steps": data.get("steps", []),
                "final_answer": data.get("final_answer", ""),
                "tools_used": tools_used,
                "confidence": float(data.get("confidence", 0.5)),
                "corrections_made": data.get("corrections_made", []),
            }
        except (json.JSONDecodeError, ValueError):
            pass

        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return {
                    "steps": data.get("steps", []),
                    "final_answer": data.get("final_answer", ""),
                    "tools_used": tools_used,
                    "confidence": float(data.get("confidence", 0.5)),
                    "corrections_made": data.get("corrections_made", []),
                }
            except (json.JSONDecodeError, ValueError):
                pass

        return default


# ---------------------------------------------------------------------------
# Entry Point — Quick Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = RefinerAgent()

    failed = {
        "steps": [
            "I think x^2 - 5x + 6 = (x-1)(x-6)",
            "So the roots are x=1 and x=6",
        ],
        "final_answer": "x = 1, x = 6",
        "confidence": 0.7,
    }
    issues = [
        {
            "step_index": 1,
            "issue": "Factorization is wrong: (x-1)(x-6) = x^2 - 7x + 6, not x^2 - 5x + 6",
            "severity": "high",
        }
    ]

    print("=" * 60)
    print("Refiner Agent — Test: fix wrong factorization")
    print("=" * 60)

    result = agent.refine(
        problem_text="Solve x^2 - 5x + 6 = 0",
        topic="algebra",
        failed_solution=failed,
        verifier_issues=issues,
    )

    print("\nCorrected Steps:")
    for i, step in enumerate(result["steps"], 1):
        print(f"  {i}. {step}")
    print(f"\nFinal Answer: {result['final_answer']}")
    print(f"Confidence:   {result['confidence']:.2f}")
    if result["corrections_made"]:
        print("\nCorrections Made:")
        for c in result["corrections_made"]:
            print(f"  - {c}")

    print(f"\nTrace duration: {agent.tracer.total_duration_ms():.0f}ms")
