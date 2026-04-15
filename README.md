# Cod-ai

This repository contains two projects:

1. **[Cod-ai CLI](#cod-ai)** — a minimal command-line AI coding assistant powered by Claude
2. **[MOOC Platform](docs/mooc-platform.md)** — an Arabic-first open-course platform aligned
   with Saudi Arabia's National eLearning Center (NELC) Excellence Standards

## MOOC Platform quick start

```bash
pip install -e .
python -m mooc --seed --reload
# open http://127.0.0.1:8000
```

See **[docs/mooc-platform.md](docs/mooc-platform.md)** for the full reference,
including the NELC taxonomy (8 domains / 43 subdomains / 339 criteria),
the student / teacher / admin portals, lesson types, assessment engine, and
the course quality-review workflow.

---

## Cod-ai

A minimal command-line AI coding assistant powered by the [Claude API](https://docs.claude.com/).

Cod-ai gives you a terminal chat with Claude that's aware of a working
directory: you can ask questions about your code, request explanations, and
have Claude generate or review snippets without leaving the shell.

## Features

- Interactive REPL backed by the Anthropic Python SDK
- System prompt tailored for software-engineering tasks
- Prompt caching on the system prompt so repeated turns stay cheap
- Optional one-shot mode (`cod-ai "your question"`) for quick queries
- Reads an `ANTHROPIC_API_KEY` from the environment or a local `.env`

## Installation

```bash
git clone https://github.com/alkatery/Cod-ai.git
cd Cod-ai
pip install -e .
```

Requires Python 3.10+.

## Configuration

Set your API key before running:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or drop it into a `.env` file at the repo root (it's gitignored):

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

Interactive mode:

```bash
cod-ai
```

One-shot mode:

```bash
cod-ai "Explain what this repo does"
```

Inside the REPL, type `/exit` or `Ctrl-D` to quit, and `/reset` to clear the
conversation history.

## Model

Cod-ai defaults to `claude-sonnet-4-6` for a good balance of quality and speed.
Override it with the `COD_AI_MODEL` environment variable:

```bash
COD_AI_MODEL=claude-opus-4-6 cod-ai
```

## License

MIT. See [LICENSE](LICENSE).
