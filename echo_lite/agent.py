"""Agent loop, Message dataclass, and run() function."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from echo_lite.tools import ToolError, dispatch


@dataclass
class Message:
    role: str
    content: str


def run(
    task: str,
    model: Callable[[list[Message]], str] | None = None,
    max_steps: int = 5,
    log_dir: str = "runs",
) -> str:
    """Run the agent loop until a final answer is given."""
    if model is None:
        from echo_lite.model import FakeModel
        model = FakeModel()

    # Create a unique log file for this run
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    log_file = Path(log_dir) / f"{timestamp}.jsonl"

    messages = [Message("user", task)]

    for step in range(1, max_steps + 1):
        # Log that we are calling the model
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"step": step, "type": "model_call"}) + "\n")
        
        raw_reply = model(list(messages))

        try:
            data = json.loads(raw_reply)
        except json.JSONDecodeError:
            raise ToolError(f"Model returned invalid JSON: {raw_reply}")

        # If model gave a final answer
        if isinstance(data, dict) and "final" in data:
            return str(data["final"])

        # If model asked to use a tool
        if isinstance(data, dict) and "tool" in data and "arg" in data:
            tool_name = str(data["tool"])
            tool_arg = str(data["arg"])
            
            try:
                result = dispatch(tool_name, tool_arg)
            except ToolError as e:
                result = f"ERROR: {e}"  # Send error back to model as text
                
            messages.append(Message("tool", result))
        else:
            raise ToolError("Model reply must have 'final' or 'tool'.")

    raise ToolError(f"Exceeded max_steps={max_steps}")