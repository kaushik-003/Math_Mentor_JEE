"""
SymPy Math Tool Layer.
Wrapper functions for symbolic math operations used by the Solver Agent.
All functions accept string inputs (LLM output) and return a standard result dict.
"""

import sympy  # type: ignore[import-untyped]
from sympy import (
    sympify, symbols, Symbol, solve, diff, integrate, limit,
    simplify, Matrix, factorial, binomial, Rational, S, oo, pi, E,
    sin, cos, tan, exp, log, sqrt,
)
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application  # type: ignore[import-untyped]


# Transformations for more natural input parsing (e.g. "2x" → "2*x")
_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)

# Safe namespace for sympify — exposes all symbols the LLM might use
_SYMPY_NAMESPACE = {
    "factorial": factorial,
    "binomial": binomial,
    "Rational": Rational,
    "S": S,
    "oo": oo,
    "pi": pi,
    "E": E,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "exp": exp,
    "log": log,
    "sqrt": sqrt,
}


def _parse(expr_str: str):
    """Parse a string into a SymPy expression. Raises on failure."""
    return parse_expr(expr_str, local_dict=_SYMPY_NAMESPACE, transformations=_TRANSFORMATIONS)


def solve_equation(equation_str: str) -> dict:
    """
    Solve an algebraic equation (expressed as LHS = 0) for all its roots.

    Args:
        equation_str: Expression string equal to zero, e.g. "x**2 - 5*x + 6"

    Returns:
        {"success": True, "result": "[2, 3]", "error": ""}
    """
    try:
        expr = _parse(equation_str)
        free = expr.free_symbols
        if not free:
            return {"success": False, "result": "", "error": "No variables found in expression."}
        # Solve w.r.t. all free symbols; if multiple, sort for determinism
        var_list = sorted(free, key=str)
        solutions = solve(expr, var_list if len(var_list) > 1 else var_list[0])
        return {"success": True, "result": str(solutions), "error": ""}
    except Exception as e:
        return {"success": False, "result": "", "error": str(e)}


def differentiate(expr_str: str, variable: str) -> dict:
    """
    Compute the derivative of an expression with respect to a variable.

    Args:
        expr_str: Expression to differentiate, e.g. "x**3 + 2*x"
        variable: Variable name, e.g. "x"

    Returns:
        {"success": True, "result": "3*x**2 + 2", "error": ""}
    """
    try:
        expr = _parse(expr_str)
        var = Symbol(variable)
        result = diff(expr, var)
        return {"success": True, "result": str(result), "error": ""}
    except Exception as e:
        return {"success": False, "result": "", "error": str(e)}


def integrate_expr(expr_str: str, variable: str) -> dict:
    """
    Compute the indefinite integral of an expression.

    Args:
        expr_str: Expression to integrate, e.g. "3*x**2 + 2"
        variable: Variable of integration, e.g. "x"

    Returns:
        {"success": True, "result": "x**3 + 2*x", "error": ""}
    """
    try:
        expr = _parse(expr_str)
        var = Symbol(variable)
        result = integrate(expr, var)
        return {"success": True, "result": str(result), "error": ""}
    except Exception as e:
        return {"success": False, "result": "", "error": str(e)}


def compute_limit(expr_str: str, variable: str, point: str) -> dict:
    """
    Evaluate the limit of an expression as a variable approaches a point.

    Args:
        expr_str: Expression, e.g. "sin(x)/x"
        variable: Variable name, e.g. "x"
        point: Limit point, e.g. "0", "oo", "pi"

    Returns:
        {"success": True, "result": "1", "error": ""}
    """
    try:
        expr = _parse(expr_str)
        var = Symbol(variable)
        pt = _parse(point)
        result = limit(expr, var, pt)
        return {"success": True, "result": str(result), "error": ""}
    except Exception as e:
        return {"success": False, "result": "", "error": str(e)}


def simplify_expr(expr_str: str) -> dict:
    """
    Simplify a mathematical expression.

    Args:
        expr_str: Expression to simplify, e.g. "sin(x)**2 + cos(x)**2"

    Returns:
        {"success": True, "result": "1", "error": ""}
    """
    try:
        expr = _parse(expr_str)
        result = simplify(expr)
        return {"success": True, "result": str(result), "error": ""}
    except Exception as e:
        return {"success": False, "result": "", "error": str(e)}


def matrix_determinant(matrix_list: list) -> dict:
    """
    Compute the determinant of a square matrix.

    Args:
        matrix_list: 2D list of numbers, e.g. [[1, 2], [3, 4]]

    Returns:
        {"success": True, "result": "-2", "error": ""}
    """
    try:
        mat = Matrix(matrix_list)
        result = mat.det()
        return {"success": True, "result": str(result), "error": ""}
    except Exception as e:
        return {"success": False, "result": "", "error": str(e)}


def evaluate_numeric(expr_str: str) -> dict:
    """
    Numerically evaluate a mathematical expression to a decimal.

    Args:
        expr_str: Expression, e.g. "sqrt(2) + pi"

    Returns:
        {"success": True, "result": "4.55990309931940", "error": ""}
    """
    try:
        expr = _parse(expr_str)
        result = expr.evalf()
        return {"success": True, "result": str(result), "error": ""}
    except Exception as e:
        return {"success": False, "result": "", "error": str(e)}


def compute_probability(expr_str: str) -> dict:
    """
    Evaluate combinatorics and probability expressions using exact SymPy arithmetic.

    Supports: factorial(n), binomial(n, k), Rational(p, q), and arithmetic
    combining them. Results are returned as exact fractions or decimals.

    Args:
        expr_str: Combinatorics/probability expression, e.g.
                  "binomial(10, 3) * Rational(1, 2)**10"
                  "factorial(5) / (factorial(2) * factorial(3))"
                  "Rational(3,6) * Rational(2,5)"

    Returns:
        {"success": True, "result": "15/512", "error": ""}
    """
    try:
        expr = _parse(expr_str)
        # Evaluate to simplest exact form
        result = sympy.nsimplify(expr, rational=True)
        # If it's an integer or simple fraction, keep exact; otherwise use decimal
        result_str = str(result)
        return {"success": True, "result": result_str, "error": ""}
    except Exception as e:
        return {"success": False, "result": "", "error": str(e)}


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

TOOLS: dict = {
    "solve_equation": solve_equation,
    "differentiate": differentiate,
    "integrate": integrate_expr,
    "compute_limit": compute_limit,
    "simplify_expr": simplify_expr,
    "matrix_determinant": matrix_determinant,
    "evaluate_numeric": evaluate_numeric,
    "compute_probability": compute_probability,
}


def run_tool(tool_name: str, **kwargs) -> dict:
    """
    Dispatch a tool call by name with keyword arguments.

    Returns the tool's result dict, or an error dict if the tool doesn't exist.
    """
    if tool_name not in TOOLS:
        return {
            "success": False,
            "result": "",
            "error": f"Unknown tool '{tool_name}'. Available: {list(TOOLS.keys())}",
        }
    try:
        return TOOLS[tool_name](**kwargs)
    except TypeError as e:
        return {"success": False, "result": "", "error": f"Bad arguments for '{tool_name}': {e}"}
