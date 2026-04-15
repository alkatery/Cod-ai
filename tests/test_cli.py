"""Smoke tests for the Cod-ai CLI entry point.

These tests avoid hitting the real Anthropic API; they only exercise argument
parsing and the package's public surface.
"""

from __future__ import annotations

import cod_ai
from cod_ai.cli import _build_parser


def test_version_attribute() -> None:
    assert isinstance(cod_ai.__version__, str)
    assert cod_ai.__version__


def test_parser_defaults() -> None:
    parser = _build_parser()
    args = parser.parse_args([])
    assert args.prompt == []
    assert args.no_stream is False
    assert args.model  # defaulted from COD_AI_MODEL or DEFAULT_MODEL


def test_parser_one_shot() -> None:
    parser = _build_parser()
    args = parser.parse_args(["hello", "world"])
    assert args.prompt == ["hello", "world"]


def test_parser_no_stream_flag() -> None:
    parser = _build_parser()
    args = parser.parse_args(["--no-stream", "what", "is", "2+2"])
    assert args.no_stream is True
    assert args.prompt == ["what", "is", "2+2"]
