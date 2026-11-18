from deepagents import create_deep_agent
from src.config.setting import mobile_model_config
from langchain_ollama import ChatOllama


def test_mobile_model_connect():
    model = ChatOllama(
        base_url=mobile_model_config.MOBILE_BASE_URL,
        model=mobile_model_config.MOBILE_MODEL_NAME,
    )
    agent = create_deep_agent(model=model, system_prompt="You are a helpful assistant")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Hi, say Hello World"}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    test_mobile_model_connect()
