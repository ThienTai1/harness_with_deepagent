"""Logging middleware for the agent.

Two styles are shown:

1. `AgentLoggingMiddleware` -- a class subclassing `AgentMiddleware` that
   hooks `wrap_model_call`, `after_model` and `wrap_tool_call`.
2. `@wrap_tool_call` -- the decorator style, for standalone functions.

Hooks (langchain 1.x, `langchain.agents.middleware.types.AgentMiddleware`):

- `before_agent(state, runtime)` / `after_agent` -- run once per invoke.
- `before_model(state, runtime)` / `after_model` -- run around every model
  call (e.g. inspect `state["messages"]` for tool calls the model issued).
- `wrap_model_call(request, handler)` -- intercept every LLM request; call
  `handler(request)` to run the model, or skip it to short-circuit.
- `wrap_tool_call(request, handler)` -- intercept tool execution;
  `request.tool_call` is the dict the model produced (`name`, `args`, `id`);
  call `handler(request)` to run the tool.

Register them via `create_deep_agent(..., middleware=[...])`; earlier
entries in the list are the outermost wrappers.
"""

import logging
from typing import Any

from langchain.agents.middleware import wrap_tool_call
from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command

logger = logging.getLogger(__name__)


class AgentLoggingMiddleware(AgentMiddleware):
    """Log model calls, model-requested tool calls and tool results."""

    def wrap_model_call(self, request: Any, handler: Any) -> Any:
        messages = getattr(request, "messages", None) or []
        logger.info("model_call messages=%d", len(messages))
        return handler(request)

    def after_model(self, state: dict, runtime: Any) -> None:
        messages = state.get("messages", [])
        if messages and isinstance(messages[-1], AIMessage):
            for call in messages[-1].tool_calls or []:
                logger.info(
                    "model_requested_tool name=%s id=%s args=%s",
                    call.get("name"),
                    call.get("id"),
                    call.get("args"),
                )

    def wrap_tool_call(self, request: Any, handler: Any) -> Any:
        call = request.tool_call
        logger.info(
            "tool_call_start name=%s id=%s args=%s",
            call.get("name"),
            call.get("id"),
            call.get("args"),
        )
        result = handler(request)
        logger.info(
            "tool_call_end name=%s status=%s",
            call.get("name"),
            getattr(result, "status", None),
        )
        return result


@wrap_tool_call
def log_tool_calls(request: Any, handler: Any) -> ToolMessage | Command[Any]:
    """Decorator-style standalone tool-call logger.

    The `@wrap_tool_call` decorator turns a function into an
    `AgentMiddleware`; pass the resulting objects to `create_deep_agent`.
    """
    call = request.tool_call
    logger.info("log_tool_calls: %s %s", call.get("name"), call.get("args"))
    return handler(request)


__all__ = ["AgentLoggingMiddleware", "log_tool_calls"]
