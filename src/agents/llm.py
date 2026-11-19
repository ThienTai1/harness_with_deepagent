"""The main LLM used by the coding agent.

Runs on Ollama (local). `settings` reads `.env`:

- `MODEL_NAME` -- the Ollama model tag, e.g. `qwen2.5` or `qwen3:8b`.
- `PROVIDER` -- informational here; `ChatOllama` is the Ollama client.
- `OLLAMA_BASE_URL` -- where the Ollama server listens (default
  `http://localhost:11434`; uncomment the example line to point elsewhere).
"""

from langchain_ollama import ChatOllama

from src.config.setting import settings

model = ChatOllama(
    model=settings.MODEL_NAME,
    base_url=settings.OLLAMA_BASE_URL,
    # temperature is off by default: code/editing tools want deterministic
    # behavior. Raise it for more creative chat, lower it for tighter code.
    temperature=0.0,
)
