"""Backend wiring for the deep agent.

Every file operation the agent performs goes through a `BackendProtocol`:

- `StateBackend` -- files live in the agent's LangGraph state. Ephemeral
  (per thread/conversation), but simple and always available; must be used
  inside graph execution, which the agent is.
- `FilesystemBackend` -- files on the real filesystem (pass a `root`).
- `StoreBackend` -- files in a LangGraph store (durable across threads).
- `LocalShellBackend` -- real FS plus a real `execute` shell tool.
- `CompositeBackend` -- routes paths by prefix: anything under `/memories/`
  goes to a store backend, everything else to the default.

`FilesystemPermission` rules can also be passed to `create_deep_agent` (or
to `FilesystemMiddleware`) with `mode="interrupt"`; those are merged with
`interrupt_on` and pause for human approval via HITL.
"""

from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    StateBackend,
    StoreBackend,
)

# Default backend: files live on disk (relative paths resolve against the
# process working directory). `FilesystemMiddleware` and the auto-injected
# `SkillsMiddleware`/`MemoryMiddleware` (for `skills=[...]` / `memory=[...]`)
# all use it. Swap in `StateBackend()` for an ephemeral per-thread backend,
# or a `CompositeBackend` to mix storage types.
DEFAULT_BACKEND = FilesystemBackend()


def memory_backend() -> StoreBackend:
    """A `StoreBackend` usable for durable agent memory.

    Needs a LangGraph store passed to the graph (`store=...`); without one
    the store calls raise, so wire it up before relying on it.
    """
    return StoreBackend(namespace=lambda _rt: ("deepagent", "memory"))


__all__ = [
    "DEFAULT_BACKEND",
    "CompositeBackend",
    "FilesystemBackend",
    "StateBackend",
    "StoreBackend",
    "memory_backend",
]
