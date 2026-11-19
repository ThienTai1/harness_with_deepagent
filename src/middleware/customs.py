"""Custom middleware: summarization of the conversation history.

`SummarizationMiddleware(model, backend=...)` summarizes older messages
once the context window fills, keeping the agent focused on the recent
turns. The backend persists evicted history to `/conversation_history/...`
so nothing is lost.
"""

from deepagents.middleware import SummarizationMiddleware

from src.agents.llm import model
from src.middleware.backend import DEFAULT_BACKEND

custom_summarization = SummarizationMiddleware(model, backend=DEFAULT_BACKEND)

__all__ = ["custom_summarization"]
