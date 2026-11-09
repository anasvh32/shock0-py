"""Tests for echo_lite."""

import json
import pytest
from echo_lite.agent import Message, run
from echo_lite.tools import REGISTRY, ToolError, dispatch


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("2+3*4", "14"),
        ("10/4", "2.5"),
        ("8/4", "2"),
        ("-(2+3)", "-5"),
        ("(2+3)*4", "20"),
    ],
)
def test_calc_valid(expr: str, expected: str):
    assert REGISTRY["calc"](expr) == expected


@pytest.mark.parametrize(
    "expr",
    ["1/0", "abc", "2+", "()", "__import__('os')", "2**3", ""],
)
def test_calc_invalid(expr: str):
    with pytest.raises(ToolError):
        REGISTRY["calc"](expr)


def test_word_count_and_utc_now():
    assert REGISTRY["word_count"]("سلام دنیا hello") == "3"
    assert REGISTRY["utc_now"]("").endswith("Z")


def test_dispatch_unknown_tool():
    with pytest.raises(ToolError):
        dispatch("nope", "x")


def test_run_with_fake_model(tmp_path):
    answer = run("what is 12*7 and the time in UTC?", log_dir=str(tmp_path))
    assert "84" in answer
    assert "UTC" in answer


def test_model_sees_tool_result(tmp_path):
    # A simple scripted model using a list iterator
    replies = iter([
        json.dumps({"tool": "calc", "arg": "1+1"}),
        json.dumps({"final": "done"}),
    ])
    def model(messages: list[Message]) -> str:
        return next(replies)

    assert run("x", model=model, log_dir=str(tmp_path)) == "done"


def test_max_steps_exceeded(tmp_path):
    def endless_tool(messages: list[Message]) -> str:
        return json.dumps({"tool": "calc", "arg": "1+1"})

    with pytest.raises(ToolError, match="max_steps"):
        run("x", model=endless_tool, max_steps=3, log_dir=str(tmp_path))


def test_log_file_created(tmp_path):
    run("what is 2+2?", log_dir=str(tmp_path))
    files = list(tmp_path.glob("*.jsonl"))
    assert len(files) == 1
    
    lines = files[0].read_text(encoding="utf-8").splitlines()
    first_line = json.loads(lines[0])
    assert "step" in first_line
    assert "type" in first_line