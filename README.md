# test-deepagent

A coding agent built on top of [`deepagents`](https://docs.langchain.com/oss/python/deepagents)
(`create_deep_agent`), running any LLM through Ollama locally.

## Quick start

```bash
uv run python src/agents/agent.py     # interactive chat, with HITL approvals
uv run python examples/hitl_demo.py   # scripted HITL demo (custom tool)
uv run pytest -q                      # full test suite (no Ollama needed)
```

In the interactive session (`src/agents/agent.py`), type a task and press Enter.
The agent replies; keep chatting — context is preserved per thread (`thread_id`
checkpoints). `/exit` (or Ctrl-D) quits. When a gated tool needs approval, the
agent prints the action and asks you to approve/edit/reject before it runs.

## Skills & memory

- **Skills** live in `skills/<name>/SKILL.md` (YAML frontmatter `name` must
  match the directory name; `description` explains when to use it). The
  agent injects a skill index into the system prompt; the model invokes a
  skill by name (e.g. `/code-review`), or you can pin names via
  `agent.invoke({"messages": [...]}, config, pinned_skills=["code-review"])`.
- **Memory** lives in `AGENTS.md` at the repo root (see `AGENTS.md` itself —
  it is the project's living memory for the agent).

Both load through the agent's backend: `create_deep_agent` is given
`backend=FilesystemBackend()` (see `src/middleware/backend.py`), so
`./skills/` and `./AGENTS.md` are read from disk on every run. To use an
ephemeral per-thread backend instead, set `backend=StateBackend()` and
pre-populate files with `agent.invoke({"messages": [...], "files": {...}})`.

Model config lives in `.env` (see `.env.sample`):

- `MODEL_NAME` – the Ollama tag (e.g. `qwen2.5`, `qwen3:8b`)
- `OLLAMA_BASE_URL` – default `http://localhost:11434`; change it if the
  Ollama server listens elsewhere

## The agent

`src/agents/agent.py` builds the agent:

```python
agent = create_deep_agent(
    model=model,                       # ChatOllama, from src/agents/llm.py
    system_prompt="You are a coding agent",
    memory=["./AGENTS.md"],
    skills=["./skills/"],
    middleware=[AgentLoggingMiddleware(), FilesystemMiddleware(backend=backend, tools="all")],
    interrupt_on=DEFAULT_INTERRUPT_ON,  # HITL policy, see below
    checkpointer=InMemorySaver(),       # required for HITL interrupts
)
```

`run_with_approval(prompt, thread_id="coding-agent")` runs it and loops on
interrupts: it prints each gated action, asks you to approve / edit / reject,
and resumes the agent with `Command(resume={"decisions": [...]})` until the
run finishes. Give each conversation its own `thread_id` if you want
checkpoints to be separate (with `InMemorySaver`, state dies with the
process; swap in a durable `InMemorySaver` → e.g. `SqliteSaver`/`PostgresSaver`
from `langgraph.checkpoint` for persistence).

## Middleware

Deep agents are configured with `langchain.agents.middleware.AgentMiddleware`
subclasses (or the `@decorator` style). The hooks you'll use most:

| Hook | When it runs | Example (see `src/middleware/logging.py`) |
|---|---|---|
| `before_agent` / `after_agent` | once per invoke | startup/shutdown side effects |
| `before_model` / `after_model` | around every model call | inspect `state["messages"]` |
| `wrap_model_call(request, handler)` | intercept every LLM request | logging, caching, fallbacks; call `handler(request)` to run the model |
| `wrap_tool_call(request, handler)` | intercept tool execution | `request.tool_call` has `name`/`args`/`id`; `handler(request)` runs the tool |
| `state_schema` | add private state keys | summarization events, metrics |

Existing middleware to wire in (`src/middleware/`):

- `AgentLoggingMiddleware` – logs model calls, requested tools, tool results.
- `customs.py` – `SummarizationMiddleware` (needs `model` + `backend`).
- `hitl.py` – the `DEFAULT_INTERRUPT_ON` policy.

Write your own:

```python
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware import wrap_tool_call

class GuardrailMiddleware(AgentMiddleware):
    def wrap_tool_call(self, request, handler):
        if request.tool_call["name"] == "shell" and "rm -rf" in str(request.tool_call["args"]):
            return ToolMessage(content="blocked", tool_call_id=request.tool_call["id"], status="error")
        return handler(request)

@wrap_tool_call                                   # decorator style
def log_calls(request, handler):
    print("calling", request.tool_call["name"])
    return handler(request)
```

## Backends

Filesystem tools route through a `BackendProtocol` (`src/middleware/backend.py`):

- `StateBackend` – default; files live in agent state (ephemeral per thread).
- `FilesystemBackend(root=...)` – real files on disk; agent edits are visible.
- `StoreBackend` – durable files in a LangGraph store.
- `LocalShellBackend` – real FS + real `execute` shell (needs sandbox config).
- `CompositeBackend(default=..., routes={"/memories/": store_backend})` – mix them.

`FilesystemPermission(operations=["write"], paths=["/secrets/**"], mode="allow" | "deny" | "interrupt")`
rules passed to `create_deep_agent(permissions=[...])` are merged with
`interrupt_on`; `mode="interrupt"` pauses for HITL approval.

## Human-in-the-loop

Two ways to enable it:

1. `create_deep_agent(interrupt_on={tool_name: True | {"allowed_decisions": [...]}})`
2. `HumanInTheLoopMiddleware(interrupt_on=...)` passed in `middleware=[...]`

Policy (`src/middleware/hitl.py`): map tool name to `True` (all decisions
allowed: `approve`/`edit`/`reject`/`respond`), a subset via
`InterruptOnConfig`, or `False` to auto-approve. Tools without an entry run
free. A `when=` predicate can decide per-call.

Flow:

```python
result = agent.invoke({"messages": [...]}, config)   # returns when an interrupt fires
# read payload: result["__interrupt__"][0].value["action_requests"]  (langchain v1)
#            or agent.get_state(config).tasks[0].interrupts           (v2/langgraph)
result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config)
```

Decisions: `{"type": "approve"}`, `{"type": "edit", "edited_action": {"name": ..., "args": {...}}}`,
`{"type": "reject", "message": "..."}`, `{"type": "respond", "message": "..."}`.

`interrupt_mode="per_call"` (langchain ≥1.4) interrupts once per gated call
with its own ID; resume with `{id: decision}` keyed by interrupt ID.

## Tests

`test/test_hitl.py` drives the agent with a fake model (`GenericFakeChatModel`
subclass that implements `bind_tools`), so HITL is verified without a running
Ollama. Covers: pause-and-approve, reject (tool blocked), and no-gating when
the tool isn't in `interrupt_on`.

## Files

```
src/
  agents/        agent.py (main), llm.py (ChatOllama), core/ (prompts)
  middleware/    backend.py, hitl.py, logging.py, customs.py
  config/        setting.py (.env), models.py (model registry)
  tools/         internal (file/api/web/db) + external (MCP)
  model_manager/ factory/registry/router/health/fallback
examples/        hitl_demo.py
test/            test_hitl.py
```
