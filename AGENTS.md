# AGENTS.md — test-deepagent

Coding agent project: langchain/deepagents (`create_deep_agent`) with an
Ollama-backed LLM (see `.env`: `MODEL_NAME`, `OLLAMA_BASE_URL`).

## Architecture

- `src/agents/agent.py` — the main agent. `run_with_approval(prompt, thread_id)`
  loops HITL interrupts until the run finishes.
- `src/agents/llm.py` — `ChatOllama` built from `.env` settings.
- `src/middleware/` — shared agent pieces:
  - `backend.py` — `FilesystemBackend` (the default; files live on disk).
  - `hitl.py` — `DEFAULT_INTERRUPT_ON` approval policy.
  - `logging.py` — `AgentLoggingMiddleware` (wrap_tool_call / wrap_model_call).
  - `customs.py` — `SummarizationMiddleware` for long conversations.
- `src/tools/` — internal file/api/web/db tools; `src/tools/external/mcp.py` — MCP.
- `src/model_manager/` — model registry/factory/router helpers.
- `test/` — pytest suite. `examples/hitl_demo.py` — scripted HITL demo.

## Commands

```bash
uv run python src/agents/agent.py     # interactive coding session (with HITL)
uv run python examples/hitl_demo.py   # HITL demo with a custom tool
uv run pytest -q                      # run the test suite
```

## Conventions

- Python 3.13. Absolute imports from the repo root (`from src...`).
- Type hints on public functions; docstrings with Args/Returns where useful.
- HITL: `write_file`/`edit_file`/`delete` are gated, reads are not.
- Middleware hooks used: `wrap_model_call`, `wrap_tool_call`, `after_model`,
  `before_agent` — see `src/middleware/logging.py` for examples.
- Don't commit the `.venv`; `AGENTS.md` here is the agent's memory of the project.

## Skills

Skills are markdown instructions the agent invokes on demand
(`/code-review`, `/write-tests`, `/python-conventions`). Add a new one by
adding a directory under `skills/` with a `SKILL.md` whose YAML frontmatter
`name` matches the directory name and has a `description`.
