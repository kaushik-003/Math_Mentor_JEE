"""
Solver Agent.
Uses GPT-4o with OpenAI function calling to solve JEE math problems step by step.
All arithmetic is delegated to SymPy tools — the LLM never computes numbers itself.
"""

import json
import sys
from typing import Any, cast

import openai

import config
from utils.trace import AgentTracer
from tools.sympy_tools import run_tool

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Max back-and-forth tool call rounds per problem (not API retries)
MAX_TOOL_ROUNDS = 10

# ---------------------------------------------------------------------------
# OpenAI Function Schemas
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "solve_equation",
            "description": (
                "Solve an algebraic equation (LHS expressed as equal to zero) for all roots. "
                "Use for any equation-solving step."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "equation_str": {
                        "type": "string",
                        "description": (
                            "Equation as a SymPy expression set equal to zero. "
                            "e.g. 'x**2 - 5*x + 6' to solve x^2 - 5x + 6 = 0"
                        ),
                    }
                },
                "required": ["equation_str"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "differentiate",
            "description": "Compute the derivative of an expression with respect to a variable.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expr_str": {
                        "type": "string",
                        "description": "Expression to differentiate, e.g. 'x**3 * sin(x)'",
                    },
                    "variable": {
                        "type": "string",
                        "description": "Variable name, e.g. 'x'",
                    },
                },
                "required": ["expr_str", "variable"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "integrate",
            "description": "Compute the indefinite integral of an expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expr_str": {
                        "type": "string",
                        "description": "Expression to integrate, e.g. '3*x**2 + 2*x'",
                    },
                    "variable": {
                        "type": "string",
                        "description": "Variable of integration, e.g. 'x'",
                    },
                },
                "required": ["expr_str", "variable"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_limit",
            "description": "Evaluate the limit of an expression as a variable approaches a point.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expr_str": {
                        "type": "string",
                        "description": "Expression, e.g. 'sin(x)/x'",
                    },
                    "variable": {
                        "type": "string",
                        "description": "Variable name, e.g. 'x'",
                    },
                    "point": {
                        "type": "string",
                        "description": "Limit point as a string, e.g. '0', 'oo', 'pi/2'",
                    },
                },
                "required": ["expr_str", "variable", "point"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simplify_expr",
            "description": "Simplify a mathematical expression to its simplest form.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expr_str": {
                        "type": "string",
                        "description": "Expression to simplify, e.g. 'sin(x)**2 + cos(x)**2'",
                    }
                },
                "required": ["expr_str"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "matrix_determinant",
            "description": "Compute the determinant of a square matrix.",
            "parameters": {
                "type": "object",
                "properties": {
                    "matrix_list": {
                        "type": "array",
                        "description": "2D array of numbers, e.g. [[1, 2], [3, 4]]",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                        },
                    }
                },
                "required": ["matrix_list"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_numeric",
            "description": (
                "Numerically evaluate a mathematical expression to a decimal. "
                "Use for final numeric simplification after symbolic steps."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expr_str": {
                        "type": "string",
                        "description": "Expression, e.g. 'sqrt(2) + pi' or '3/7'",
                    }
                },
                "required": ["expr_str"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_probability",
            "description": (
                "Evaluate combinatorics and probability expressions using exact arithmetic. "
                "Supports factorial(n), binomial(n,k), Rational(p,q), and arithmetic combining them. "
                "Use this for ALL probability, counting, and permutation/combination problems."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expr_str": {
                        "type": "string",
                        "description": (
                            "Combinatorics/probability expression. "
                            "e.g. 'binomial(10,3) * Rational(1,2)**10' "
                            "or 'factorial(5) / (factorial(2)*factorial(3))' "
                            "or 'Rational(3,6) * Rational(2,5)'"
                        ),
                    }
                },
                "required": ["expr_str"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a JEE Advanced mathematics expert and solver.

RULES (follow strictly):
1. Solve every problem step by step, explaining your reasoning clearly.
2. NEVER compute arithmetic, algebra, calculus, or probability yourself — always call the provided tools.
3. Use tools for every calculation: factoring, derivatives, integrals, limits, determinants, probability/combinatorics.
4. For probability problems, always use compute_probability with factorial(), binomial(), or Rational().
5. After all tool calls are complete, respond ONLY with a valid JSON object in exactly this format:

{
  "steps": [
    "Step 1: <explanation of what you did and the tool result>",
    "Step 2: ...",
    ...
  ],
  "final_answer": "<concise final answer, e.g. 'x = 2, x = 3' or '6x^2 + 2'>",
  "confidence": <float between 0.0 and 1.0>
}

Do not include any text outside this JSON object in your final response."""


# ---------------------------------------------------------------------------
# Solver Agent
# ---------------------------------------------------------------------------

class SolverAgent:
    """
    Solver Agent that uses GPT-4o with function calling to solve math problems.
    Delegates all computation to SymPy tools via the tool call loop.
    """

    def __init__(self, tracer: AgentTracer | None = None):
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.tracer = tracer or AgentTracer()
        self.model = config.LLM_MODEL

    def solve(
        self,
        problem_text: str,
        topic: str,
        rag_context: list[str] | None = None,
    ) -> dict:
        """
        Solve a math problem using GPT-4o + SymPy tools.

        Args:
            problem_text: The problem statement as a string.
            topic: One of config.SUPPORTED_TOPICS, e.g. "algebra", "calculus".
            rag_context: Optional list of reference strings from the RAG system.

        Returns:
            {
                "steps": [...],
                "final_answer": "...",
                "tools_used": [{"tool": "...", "input": {...}, "output": {...}}, ...],
                "confidence": 0.9,
            }
        """
        self.tracer.start("SolverAgent")
        tools_used: list[dict] = []

        # Build user message
        user_msg = self._build_user_message(problem_text, topic, rag_context or [])
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]

        # Tool call loop
        last_error = None
        for round_num in range(MAX_TOOL_ROUNDS):
            try:
                response = self._call_api(messages)
            except Exception as e:
                last_error = str(e)
                break

            msg = response.choices[0].message

            if msg.tool_calls:
                # Append assistant message (with tool_calls) to history
                messages.append(msg)

                # Execute each requested tool and append results
                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError as e:
                        args = {}
                        tool_result = {"success": False, "result": "", "error": f"Bad JSON args: {e}"}
                    else:
                        tool_result = run_tool(tool_name, **args)

                    tools_used.append({
                        "tool": tool_name,
                        "input": args,
                        "output": tool_result,
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(tool_result),
                    })

                # Continue loop to let GPT-4o process tool results
                continue

            # No tool calls — this is the final answer
            answer = self._parse_final_response(msg.content)
            answer["tools_used"] = tools_used

            self.tracer.end(
                input_summary=f"[{topic}] {problem_text[:80]}",
                output_summary=answer.get("final_answer", ""),
                metadata={"rounds": round_num + 1, "tools_called": len(tools_used)},
            )
            return answer

        # Exhausted rounds or API error
        error_result = {
            "steps": [f"Solver failed after {MAX_TOOL_ROUNDS} rounds. Last error: {last_error}"],
            "final_answer": "Could not determine answer.",
            "tools_used": tools_used,
            "confidence": 0.0,
        }
        self.tracer.end(
            input_summary=f"[{topic}] {problem_text[:80]}",
            output_summary="FAILED",
            metadata={"error": last_error},
        )
        return error_result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _call_api(self, messages: list[dict[str, Any]]) -> Any:
        """
        Call the OpenAI API with retries on transient failures.
        Uses config.MAX_SOLVER_RETRIES for API-level retry attempts.
        """
        last_exc = None
        for attempt in range(config.MAX_SOLVER_RETRIES + 1):
            try:
                return self.client.chat.completions.create(
                    model=self.model,
                    temperature=config.LLM_TEMPERATURE,
                    messages=cast(Any, messages),
                    tools=cast(Any, TOOL_SCHEMAS),
                    tool_choice="auto",
                )
            except (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError) as e:
                last_exc = e
                if attempt < config.MAX_SOLVER_RETRIES:
                    continue
            except openai.APIError as e:
                raise  # Non-transient errors bubble up immediately
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("OpenAI call failed with no captured exception.")

    def _build_user_message(self, problem_text: str, topic: str, rag_context: list[str]) -> str:
        """Construct the user message with problem and optional RAG context."""
        lines = [
            f"Topic: {topic}",
            f"Problem: {problem_text}",
        ]
        if rag_context:
            lines.append("\nRelevant reference material:")
            for i, chunk in enumerate(rag_context, 1):
                lines.append(f"[{i}] {chunk.strip()}")
        lines.append("\nSolve this problem step by step using the available tools.")
        return "\n".join(lines)

    def _parse_final_response(self, content: str) -> dict:
        """
        Parse the final JSON response from the model.
        Falls back gracefully if the model doesn't produce valid JSON.
        """
        if not content:
            return {"steps": [], "final_answer": "", "confidence": 0.0}

        # Try direct JSON parse
        try:
            data = json.loads(content)
            return {
                "steps": data.get("steps", []),
                "final_answer": data.get("final_answer", ""),
                "confidence": float(data.get("confidence", 0.5)),
            }
        except json.JSONDecodeError:
            pass

        # Try to extract JSON block from fenced markdown or surrounding text
        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return {
                    "steps": data.get("steps", []),
                    "final_answer": data.get("final_answer", ""),
                    "confidence": float(data.get("confidence", 0.5)),
                }
            except json.JSONDecodeError:
                pass

        # Last resort: return raw content as a single step
        return {
            "steps": [content],
            "final_answer": content.strip().splitlines()[-1] if content.strip() else "",
            "confidence": 0.3,
        }


# ---------------------------------------------------------------------------
# Terminal Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Allow running from project root or agents/ directory
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    from agents.router_agent import RouterAgent
    from rag.retriever import Retriever

    TEST_PROBLEMS = [
        "Find all real solutions to x**2 - 5*x + 6 = 0.",
        (
            "Differentiate f(x) = x**3 * sin(x) with respect to x, "
            "then simplify the result."
        ),
        (
            "A bag contains 3 red balls and 2 blue balls. "
            "Two balls are drawn at random without replacement. "
            "What is the probability that both balls are red?"
        ),
    ]

    router = RouterAgent()
    retriever = Retriever()
    solver = SolverAgent()

    for i, problem_text in enumerate(TEST_PROBLEMS, 1):
        print(f"\n{'='*60}")
        print(f"Problem {i}")
        print(f"  {problem_text}")
        print("="*60)

        # Step 1: Classify topic
        print("\n[Router Agent]")
        classification = router.classify(problem_text)
        topic = classification["topic"] or "algebra"  # fallback
        print(f"  Topic    : {classification['topic']}")
        print(f"  Subtopic : {classification['subtopic']}")
        print(f"  Reasoning: {classification['reasoning']}")

        # Step 2: Retrieve RAG context
        print("\n[RAG Retriever]")
        raw_results = retriever.search(problem_text, topic=classification["topic"])
        if raw_results:
            print(f"  Found {len(raw_results)} chunks (top scores):")
            for r in raw_results[:2]:
                preview = r["text"][:120].replace("\n", " ")
                print(f"    [{r['score']:.3f}] {r['source']}: {preview}...")
            rag_context = [r["text"] for r in raw_results]
        else:
            print("  No RAG context found (run rag/embedder.py to populate).")
            rag_context = []

        # Step 3: Solve with RAG context
        print("\n[Solver Agent]")
        result = solver.solve(
            problem_text=problem_text,
            topic=topic,
            rag_context=rag_context,
        )

        print("\nSteps:")
        for j, step in enumerate(result["steps"], 1):
            print(f"  {j}. {step}")

        print(f"\nFinal Answer: {result['final_answer']}")
        print(f"Confidence:   {result['confidence']}")

        if result["tools_used"]:
            print("\nTools Used:")
            for t in result["tools_used"]:
                status = "OK" if t["output"].get("success") else "FAIL"
                print(f"  [{status}] {t['tool']} -> {t['output'].get('result') or t['output'].get('error')}")
        else:
            print("\nTools Used: none")

    # Print combined trace summary
    print(f"\n{'='*60}")
    print("Agent Trace Summary")
    print("="*60)

    all_tracers = [
        ("Router", router.tracer),
        ("Solver", solver.tracer),
    ]
    total_ms = 0.0
    for agent_label, tracer in all_tracers:
        for step in tracer.get_steps():
            print(f"  [{agent_label}] {step.agent_name}")
            print(f"    Input  : {step.input_summary}")
            print(f"    Output : {step.output_summary}")
            print(f"    Time   : {step.duration_ms:.1f}ms")
            print(f"    Meta   : {step.metadata}")
            print()
        total_ms += tracer.total_duration_ms()

    print(f"Total duration: {total_ms:.1f}ms")
