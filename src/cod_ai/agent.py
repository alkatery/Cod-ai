"""Agent wrapper around the Anthropic Messages API.

The system prompt is marked with ``cache_control`` so that repeated turns in a
REPL session hit the Anthropic prompt cache. That keeps latency and token cost
low even for long-running sessions.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterator

import anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 2048

SYSTEM_PROMPT = """You are Cod-ai, a concise and precise AI coding assistant \
running in the user's terminal.

Guidelines:
- Answer software-engineering questions directly and accurately.
- When showing code, use fenced code blocks with the correct language tag.
- Prefer small, focused examples over long monologues.
- If a question is ambiguous, ask one clarifying question before guessing.
- Never fabricate APIs, flags, or file contents. If you don't know, say so.
- Assume the user is a working developer; skip beginner-level preamble.
"""


@dataclass
class Agent:
    """Stateful chat agent that talks to the Claude API."""

    model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS
    api_key: str | None = None
    _client: anthropic.Anthropic = field(init=False)
    _history: list[dict] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Export it or add it to a .env file."
            )
        self._client = anthropic.Anthropic(api_key=key)

    # ------------------------------------------------------------------ state

    def reset(self) -> None:
        """Drop all conversation history."""
        self._history.clear()

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    # --------------------------------------------------------------- messaging

    def _system_blocks(self) -> list[dict]:
        # Marking the system prompt as ephemeral cached lets the API reuse
        # the prefill across subsequent requests in the same session.
        return [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def send(self, user_message: str) -> str:
        """Send a user turn and return the assistant's full reply as a string."""
        self._history.append({"role": "user", "content": user_message})
        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self._system_blocks(),
            messages=self._history,
        )
        reply = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def stream(self, user_message: str) -> Iterator[str]:
        """Send a user turn and yield assistant text chunks as they arrive."""
        self._history.append({"role": "user", "content": user_message})
        collected: list[str] = []
        with self._client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self._system_blocks(),
            messages=self._history,
        ) as stream:
            for text in stream.text_stream:
                collected.append(text)
                yield text
        self._history.append({"role": "assistant", "content": "".join(collected)})
