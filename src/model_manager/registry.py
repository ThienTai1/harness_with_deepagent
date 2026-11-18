from os import terminal_size

from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama


class ModelRegistry(BaseModel):
    base_url: str | None = None
    model: str | None = "qwen2.5"
    temperature: float | None = 0.3

    def get_model(self, base_url, model, temperature):
        model = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=temperature,
        )
        return model
