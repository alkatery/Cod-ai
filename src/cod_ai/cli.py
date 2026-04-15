"""Command-line entry point for Cod-ai."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Sequence

from dotenv import load_dotenv

from . import __version__
from .agent import DEFAULT_MODEL, Agent

SLASH_HELP = """Slash commands:
  /help    Show this message
  /reset   Clear the current conversation history
  /exit    Quit the REPL (Ctrl-D also works)
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cod-ai",
        description="A minimal command-line AI coding assistant powered by Claude.",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="One-shot prompt. If omitted, Cod-ai starts an interactive REPL.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("COD_AI_MODEL", DEFAULT_MODEL),
        help=f"Claude model to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming output (useful for piping to other tools).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"cod-ai {__version__}",
    )
    return parser


def _run_one_shot(agent: Agent, prompt: str, stream: bool) -> int:
    if stream:
        for chunk in agent.stream(prompt):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        sys.stdout.write("\n")
    else:
        sys.stdout.write(agent.send(prompt) + "\n")
    return 0


def _run_repl(agent: Agent, stream: bool) -> int:
    print(f"Cod-ai {__version__} — model: {agent.model}")
    print("Type /help for commands, /exit or Ctrl-D to quit.\n")
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not user_input:
            continue

        if user_input in {"/exit", "/quit"}:
            return 0
        if user_input == "/help":
            print(SLASH_HELP)
            continue
        if user_input == "/reset":
            agent.reset()
            print("(history cleared)\n")
            continue

        sys.stdout.write("cod> ")
        sys.stdout.flush()
        try:
            if stream:
                for chunk in agent.stream(user_input):
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                sys.stdout.write("\n\n")
            else:
                sys.stdout.write(agent.send(user_input) + "\n\n")
        except KeyboardInterrupt:
            print("\n(interrupted)\n")
            continue


def main(argv: Sequence[str] | None = None) -> int:
    load_dotenv()
    args = _build_parser().parse_args(argv)

    try:
        agent = Agent(model=args.model)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    stream = not args.no_stream
    if args.prompt:
        return _run_one_shot(agent, " ".join(args.prompt), stream)
    return _run_repl(agent, stream)


if __name__ == "__main__":
    raise SystemExit(main())
