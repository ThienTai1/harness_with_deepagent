"""Skills + memory tests.

`create_deep_agent(backend=FilesystemBackend(), skills=["./skills/"],
memory=["./AGENTS.md"])` auto-injects `SkillsMiddleware`/`MemoryMiddleware`
onto the same backend, so both load from disk. Tests below use fake models
where the agent graph itself is exercised and call middleware hooks directly
otherwise.
"""

from typing import Any, ClassVar

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware import MemoryMiddleware, SkillsMiddleware

SKILL_NAMES = {"code-review", "write-tests", "python-conventions"}


def test_skills_load_from_disk():
    mw = SkillsMiddleware(backend=FilesystemBackend(), sources=["./skills/"])
    update = mw.before_agent({"messages": []}, None, {})
    assert update is not None
    names = {s["name"] for s in update["skills_metadata"]}
    assert SKILL_NAMES.issubset(names)
    assert update.get("skills_load_errors", []) == []


def test_memory_load_from_disk():
    mw = MemoryMiddleware(backend=FilesystemBackend(), sources=["./AGENTS.md"])
    update = mw.before_agent({"messages": []}, None, {})
    assert update is not None
    assert any("test-deepagent" in text for text in update["memory_contents"].values())


class RecordingFakeModel(GenericFakeChatModel):
    """Fake model that records every message list it receives (for prompt checks)."""

    received: ClassVar[list[list[Any]]] = []

    def bind_tools(self, tools: Any, *, tool_choice: Any = None, **kwargs: Any) -> "RecordingFakeModel":
        return self

    def _generate(self, messages: Any, stop: Any = None, run_manager: Any = None, **kwargs: Any) -> Any:
        type(self).received.append(list(messages))
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


def test_agent_injects_skills_and_memory_into_system_prompt():
    RecordingFakeModel.received = []
    model = RecordingFakeModel(messages=iter([AIMessage(content="ok")]))
    agent = create_deep_agent(
        model=model,
        backend=FilesystemBackend(),
        skills=["./skills/"],
        memory=["./AGENTS.md"],
        interrupt_on={},
        checkpointer=InMemorySaver(),
    )
    config = {"configurable": {"thread_id": "t-skills-memory"}}
    result = agent.invoke({"messages": [{"role": "user", "content": "hi"}]}, config)
    assert result["messages"][-1].content == "ok"

    prompts = [m.content for msgs in RecordingFakeModel.received for m in msgs if isinstance(m, SystemMessage)]
    blob = "\n".join(str(p) for p in prompts)
    assert "test-deepagent" in blob  # from AGENTS.md (memory)
    assert all(name in blob for name in SKILL_NAMES)  # from ./skills/ (skills)
