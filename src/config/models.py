from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    name: str
    temperature: float = 0.0
    num_ctx: int = 8192


MODELS = {
    "main": ModelConfig(
        name="qwen3:8b",
        temperature=0.0,
        num_ctx=16384,
    ),
    "fast": ModelConfig(
        name="gemma3:4b",
        temperature=0.3,
    ),
    "coder": ModelConfig(
        name="qwen2.5-coder:7b",
        temperature=0.0,
    ),
    "summarizer": ModelConfig(
        name="llama3.1:8b",
        temperature=0.2,
    ),
}
