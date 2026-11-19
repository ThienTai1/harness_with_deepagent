"""End-to-end human-in-the-loop demo.

Shows a custom tool being gated by an interrupt: the agent pauses, prints
the action it wants to take, and only runs it after the human approves.

Run:  python examples/hitl_demo.py
"""

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from deepagents import create_deep_agent

from src.agents.agent import run_with_approval
from src.agents.llm import model


@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email to a recipient (demo stub: prints instead of sending)."""
    print(f"\n[email sent] To: {recipient}\nSubject: {subject}\n---\n{body}")
    return "Email sent."


demo_agent = create_deep_agent(
    model=model,
    tools=[send_email],
    system_prompt="You are a demo agent. Use send_email when asked to mail someone.",
    # Gated: the agent must get human approval before calling send_email.
    interrupt_on={"send_email": True},
    checkpointer=InMemorySaver(),
)


if __name__ == "__main__":
    result = run_with_approval(
        "Email alice@example.com with subject 'Demo' and body 'Hello from the demo agent.'",
        agent=demo_agent,
    )
    print("\nFinal answer:", result["messages"][-1].content)
