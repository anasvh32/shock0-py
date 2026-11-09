"""Tools for echo_lite: registry, safe calc, word_count, utc_now."""

import ast
import operator
from datetime import datetime, timezone
from typing import Callable


class ToolError(Exception):
    """Raised when a tool fails or input is invalid."""
    pass


REGISTRY: dict[str, Callable[[str], str]] = {}


def tool(fn: Callable[[str], str]) -> Callable[[str], str]:
    """Decorator to register a tool by its name."""
    REGISTRY[fn.__name__] = fn
    return fn


def dispatch(name: str, arg: str) -> str:
    """Run a tool by name, raising ToolError on any problem."""
    if name not in REGISTRY:
        raise ToolError(f"Unknown tool: {name}")
    try:
        return REGISTRY[name](arg)
    except Exception as e:
        raise ToolError(str(e)) from e


# Allowed math operations for the calculator
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _evaluate(node: ast.AST) -> int | float:
    """Safely walk the AST tree and calculate the result."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_evaluate(node.operand)
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    raise ToolError("Invalid expression")


@tool
def calc(expr: str) -> str:
    """Evaluate a math expression safely (no eval)."""
    if not expr.strip():
        raise ToolError("Empty expression")
    
    # Check for invalid characters first
    allowed = "0123456789+-*/(). "
    if any(ch not in allowed for ch in expr):
        raise ToolError("Invalid characters in expression")
        
    try:
        # Parse the string into an AST, then calculate it
        tree = ast.parse(expr.strip(), mode="eval")
        result = _evaluate(tree.body)
        
        # If result is a whole number, return it without .0
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except ZeroDivisionError:
        raise ToolError("Division by zero")
    except Exception:
        raise ToolError("Invalid expression")


@tool
def word_count(text: str) -> str:
    """Count words in a text."""
    return str(len(text.split()))


@tool
def utc_now(arg: str) -> str:
    """Return current UTC time."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
