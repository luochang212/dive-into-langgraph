# -*- coding: utf-8 -*-
from fastmcp import FastMCP
import ast
import re


mcp = FastMCP("math_mcp")


def _eval_ast(node):
    """Safely evaluate a restricted arithmetic AST node."""
    if isinstance(node, ast.Expression):
        return _eval_ast(node.body)
    if isinstance(node, ast.BinOp):
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return left**right
        if isinstance(op, ast.FloorDiv):
            return left // right
        raise ValueError("Unsupported operation")
    if isinstance(node, ast.UnaryOp):
        operand = _eval_ast(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unsupported unary operation")
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported constant type")
    # For compatibility if ast.Num appears (older Python)
    if isinstance(node, ast.Num):
        return node.n
    raise ValueError("Unsupported expression element")


def _normalize_expression(text: str) -> str:
    """Normalize input to a strict arithmetic expression."""
    t = text.replace("×", "*").replace("÷", "/")

    allowed = set("0123456789.+-*/() % ")
    cleaned = []
    for ch in t:
        if ch in allowed:
            cleaned.append(ch)

    expr = "".join(cleaned)
    expr = re.sub(r"\s+", " ", expr).strip()
    return expr


@mcp.tool
def math(question: str) -> int | float:
    """Solve a natural-language arithmetic question, e.g. "what's (3 + 5) x 12?".
    Returns a number; integers are returned without a decimal.
    """
    # Security: Limit input length to prevent DoS attacks
    if len(question) > 1000:
        raise ValueError("Input too long. Maximum 1000 characters allowed.")

    expr = _normalize_expression(question)
    if not expr:
        raise ValueError("No arithmetic expression found in input")

    # Security: Further limit expression length after normalization
    if len(expr) > 200:
        raise ValueError("Expression too complex after normalization")

    try:
        parsed = ast.parse(expr, mode="eval")
        result = _eval_ast(parsed)
    except ZeroDivisionError:
        raise ValueError("Division by zero is not allowed")
    except RecursionError:
        raise ValueError("Expression too complex - recursion depth exceeded")
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression: {expr}") from e

    # Return int if it is an integer value, else float
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


if __name__ == "__main__":
    mcp.run()
