"""Run with: python -m echo_lite "question"."""

import sys

from echo_lite.agent import run
from echo_lite.tools import ToolError


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m echo_lite "your question"')
        sys.exit(1)
    try:
        print(run(" ".join(sys.argv[1:])))
    except ToolError as e:
        print("error:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
