---
name: python-conventions
description: Project Python conventions — layout, typing, style, and how to run things.
---

# Python Conventions

- Python 3.13, pyproject-managed with `uv`; always run via `uv run`.
- Absolute imports from the repo root: `from src.agents.agent import agent`.
- Public functions have type hints and docstrings (Args/Returns where useful).
- Middleware: subclass `AgentMiddleware` or use the `@wrap_tool_call` /
  `@wrap_model_call` decorators (see `src/middleware/logging.py`).
- Tests: `test/`, run with `uv run pytest -q`.
- Never commit `.venv` or the local `AGENTS.md` memory file changes
  unnecessarily; `AGENTS.md` and `skills/` are the agent's project knowledge.
