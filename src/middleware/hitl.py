"""Human-in-the-loop (HITL) policy for the agent.

Map tool name -> `True` (all decisions allowed) or `InterruptOnConfig`
(subset of `approve` / `edit` / `reject` / `respond`) or `False` (auto-run).
Tools without an entry are auto-approved.

Mutating filesystem tools are gated by default; `create_deep_agent` turns
this mapping into `HumanInTheLoopMiddleware` and pauses before each gated
call until a human resumes with a decision (see `run_with_approval` in
`src/agents/agent.py`). Filesystem permissions with `mode="interrupt"` are
merged on top of this mapping.
"""

from langchain.agents.middleware import InterruptOnConfig

DEFAULT_INTERRUPT_ON: dict[str, bool | InterruptOnConfig] = {
    "write_file": True,
    "edit_file": True,
    "delete": True,
    # `execute` only exists when the backend supports it (e.g.
    # LocalShellBackend); unknown names are simply ignored by HITL.
    "execute": {"allowed_decisions": ["approve", "reject"]},
    # Auto-approved by default (not listed): read_file, ls, glob, grep.
}

__all__ = ["DEFAULT_INTERRUPT_ON", "InterruptOnConfig"]
