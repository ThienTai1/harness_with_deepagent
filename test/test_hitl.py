"""HITL tests that don't need a running Ollama: they drive `create_deep_agent`
with a `GenericFakeChatModel` that emits scripted tool calls."""

from typing import Any

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from deepagents import create_deep_agent


class FakeToolCallingModel(GenericFakeChatModel):
    """`GenericFakeChatModel` that tolerates `bind_tools` (agent always binds)."""

    def bind_tools(self, tools: Any, *, tool_choice: Any = None, **kwargs: Any) -> "FakeToolCallingModel":
        return self


def _tool_call_then_done(tool_call_id: str = "call_1") -> FakeToolCallingModel:
    """Fake model: first call -> one `write_file` tool call; second -> text."""
    return FakeToolCallingModel(
        messages=iter(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "write_file",
                            "args": {"file_path": "/tmp/deepagent_hitl_test.txt", "content": "hello"},
                            "id": tool_call_id,
                        }
                    ],
                ),
                AIMessage(content="done"),
            ]
        )
    )


def _interrupts(result) -> list:
    if isinstance(result, dict):
        return list(result.get("__interrupt__") or [])
    return list(getattr(result, "interrupts", None) or [])


def test_hitl_pause_and_approve():
    agent = create_deep_agent(
        model=_tool_call_then_done(),
        interrupt_on={"write_file": True},
        checkpointer=InMemorySaver(),
    )
    config = {"configurable": {"thread_id": "t-hitl-approve"}}
    result = agent.invoke({"messages": [{"role": "user", "content": "write a file"}]}, config)

    interrupts = _interrupts(result)
    assert interrupts, "expected the agent to pause for approval"
    payload = interrupts[0].value
    assert payload["action_requests"][0]["name"] == "write_file"
    assert payload["action_requests"][0]["args"]["file_path"] == "/tmp/deepagent_hitl_test.txt"

    result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config)
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert tool_messages and tool_messages[0].status == "success"
    assert result["messages"][-1].content == "done"


def test_hitl_reject_stops_the_call():
    agent = create_deep_agent(
        model=_tool_call_then_done(),
        interrupt_on={"write_file": True},
        checkpointer=InMemorySaver(),
    )
    config = {"configurable": {"thread_id": "t-hitl-reject"}}
    result = agent.invoke({"messages": [{"role": "user", "content": "write a file"}]}, config)
    assert _interrupts(result)

    result = agent.invoke(
        Command(resume={"decisions": [{"type": "reject", "message": "not now"}]}), config
    )
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert tool_messages and tool_messages[0].status == "error"


def test_no_interrupt_without_gating():
    agent = create_deep_agent(
        model=_tool_call_then_done(),
        interrupt_on={"write_file": False},
        checkpointer=InMemorySaver(),
    )
    config = {"configurable": {"thread_id": "t-hitl-off"}}
    result = agent.invoke({"messages": [{"role": "user", "content": "write a file"}]}, config)
    assert not _interrupts(result)
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert tool_messages and tool_messages[0].status == "success"
    assert result["messages"][-1].content == "done"
