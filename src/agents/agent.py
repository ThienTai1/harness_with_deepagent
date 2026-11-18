"""Define a deep agent here"""

# from src.agents.core import backend
from src.tools.internal.web_tools import search_web
from src.tools.internal.file_tools import search_file_path
from src.agents.llm import model
from src.agents.core.prompts import research_instructions
from deepagents import create_deep_agent

# from deepagents.backends import StateBackend
from src.config.setting import settings


agent = create_deep_agent(
    model=model,
    system_prompt="You are a coding agent",
    tools=[search_file_path, search_web],
    memory=["./AGENTS.md"],
    skills=["./skills/"],
    # backend=StateBackend,
)


if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "where is folder harness_agent in Projects?",
                }
            ]
        }
    )

    print(result["messages"][-1].content)
