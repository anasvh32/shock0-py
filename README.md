# shock101-py / echo_lite

A tiny Agent CLI that lives in the terminal. It uses only the Python
standard library: a tool registry, a rule-based `FakeModel`, a safe
`calc` tool (no dynamic code execution) and JSONL run logs.

## Setup

```bash
uv sync
```

## Run

```bash
uv run python -m echo_lite "what is 12*7 and the time in UTC?"
# 12*7 = 84; UTC time: 2026-11-08T05:54:00Z
```

## Test

```bash
uv run pytest
```

## How it works

1. `run()` sends the task to a model (a callable that takes a list of
   `Message` and returns JSON).
2. The model answers `{"tool": "calc", "arg": "12*7"}` or `{"final": "..."}`.
3. Tool results go back to the model as `Message("tool", result)`.
4. Every run writes a log file to `runs/<timestamp>.jsonl`.

## Tools

| Tool         | What it does                                             |
|--------------|----------------------------------------------------------|
| `calc`       | `+ - * /`, parentheses, unary minus; hand-written parser |
| `word_count` | counts words in a text                                   |
| `utc_now`    | current UTC time, like `2026-11-08T05:54:00Z`            |
