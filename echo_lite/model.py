"""FakeModel: a simple rule-based model for testing."""

import json
import re
from echo_lite.agent import Message


class FakeModel:
    def __call__(self, messages: list[Message]) -> str:
        task = messages[0].content
        results = [m.content for m in messages if m.role == "tool"]

        # Find a math expression in the task
        expr_match = re.search(r"[\d(][\d\s.+\-*/()]*", task)
        expr = None
        if expr_match:
            expr = expr_match.group().strip()
            if any(op in expr for op in "+-*/"):
                expr = expr.replace(" ", "")

        # Check if it wants the time
        wants_time = bool(re.search(r"\b(time|utc)\b", task, re.IGNORECASE))

        # Decide which tool to use next
        planned_tools = []
        if expr:
            planned_tools.append(("calc", expr))
        if wants_time:
            planned_tools.append(("utc_now", ""))

        # If we haven't used all tools yet, call the next one
        if len(results) < len(planned_tools):
            name, arg = planned_tools[len(results)]
            return json.dumps({"tool": name, "arg": arg})

        # If a tool failed, return the error as the final answer
        for res in results:
            if res.startswith("ERROR"):
                return json.dumps({"final": res})

        # Otherwise, build a nice final answer
        parts = []
        if expr:
            parts.append(f"{expr} = {results[0]}")
        if wants_time:
            parts.append(f"UTC time: {results[-1]}")
            
        if not parts:
            parts.append(f"processed: {task}")
            
        return json.dumps({"final": "; ".join(parts)})