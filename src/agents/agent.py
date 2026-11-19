"""Define the deep agent here."""

import json
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from deepagents import create_deep_agent
from deepagents.middleware import FilesystemMiddleware

from src.agents.llm import model
from src.middleware.backend import DEFAULT_BACKEND
from src.middleware.hitl import DEFAULT_INTERRUPT_ON
from src.middleware.logging import AgentLoggingMiddleware

backend = DEFAULT_BACKEND

agent = create_deep_agent(
    model=model,
    system_prompt="You are a coding agent",
    backend=backend,  # FilesystemBackend -> skills/memory load from disk
    memory=["./AGENTS.md"],
    skills=["./skills/"],
    middleware=[
        AgentLoggingMiddleware(),
        # Expose the full tool set (read_file, ls, glob, grep, write_file,
        # edit_file, delete, ...). write_file/edit_file/delete are gated by
        # interrupt_on below, so mutations are reviewed before they run.
        FilesystemMiddleware(backend=backend, tools="all"),
    ],
    # Pause before gated tools run; see src/middleware/hitl.py.
    interrupt_on=DEFAULT_INTERRUPT_ON,
    # HITL is persisted per thread; required for invoke(...)/Command(resume).
    checkpointer=InMemorySaver(),
)


def _pending_interrupts(result: Any) -> list:
    """Pull interrupt payloads out of an invoke result (langchain v1/v2 shapes)."""
    if isinstance(result, dict):
        return list(result.get("__interrupt__") or [])
    return list(getattr(result, "interrupts", None) or [])


def _review_and_decide(interrupt_value: Any) -> list[dict]:
    """Print pending actions; ask the user approve/edit/reject for each.

    Returns a `HITLResponse["decisions"]` payload matched to
    `action_requests` by position.
    """
    requests = (
        interrupt_value.get("action_requests", [])
        if isinstance(interrupt_value, dict)
        else []
    )
    decisions: list[dict] = []
    for action in requests:
        name = action["name"]
        args = action.get("args", {})
        print(f"\nApproval needed: {name}({json.dumps(args, indent=2)})")
        choice = (
            input("[a]pprove / [e]dit / [r]eject (default approve): ").strip().lower()
            or "a"
        )
        if choice in ("a", "approve"):
            decisions.append({"type": "approve"})
        elif choice in ("e", "edit"):
            decisions.append(
                {"type": "edit", "edited_action": {"name": name, "args": args}}
            )
        else:
            reason = input("Rejection reason: ").strip()
            decisions.append(
                {"type": "reject", **({"message": reason} if reason else {})}
            )
    return decisions


def run_with_approval(
    prompt: str, thread_id: str = "coding-agent", agent: Any = None
) -> Any:
    """Invoke the agent, approving (or rejecting) each interrupt until done.

    Example:
        >>> result = run_with_approval("write a README for this project")
        >>> print(result["messages"][-1].content)
    """
    agent = agent or globals()["agent"]
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]}, config)
    while interrupts := _pending_interrupts(result):
        decisions: list[dict] = []
        for interrupt in interrupts:
            decisions.extend(_review_and_decide(interrupt.value))
        result = agent.invoke(Command(resume={"decisions": decisions}), config)
    return result


def _print_last_message(result: Any) -> None:
    """Print the agent's latest message text (content may be str or blocks)."""
    content = result["messages"][-1].content
    if isinstance(content, list):
        content = "\n".join(str(block) for block in content)
    print(f"\nagent: {content}\n")


def chat(thread_id: str = "coding-agent") -> None:
    """Interactive chat loop: send messages until /exit.

    Every turn is a new user message on the same thread, so the agent keeps
    the conversation context (checkpointer) and skills/memory. HITL approvals
    are handled inline via the same loop as `run_with_approval`.
    """
    config = {"configurable": {"thread_id": thread_id}}
    print("coding agent — type your task, or /exit to quit.")
    while True:
        try:
            user_input = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input in ("/exit", "/quit"):
            break
        result = agent.invoke({"messages": [{"role": "user", "content": user_input}]}, config)
        while interrupts := _pending_interrupts(result):
            decisions: list[dict] = []
            for interrupt in interrupts:
                decisions.extend(_review_and_decide(interrupt.value))
            result = agent.invoke(Command(resume={"decisions": decisions}), config)
        _print_last_message(result)


if __name__ == "__main__":
    chat()
