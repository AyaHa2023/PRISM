from __future__ import annotations

from ..data_layer.state_db import StateDatabase
from ..models.personas import AgentBase
from .llm_brain import call_llm


def ask_agent(
    agent: AgentBase,
    question: str,
    db: StateDatabase | None = None,
    use_mock: bool = True,
    model: str = "llama3.1:latest",
) -> dict:
    memory = db.build_agent_context(agent.name) if db else ""
    response = call_llm(
        agent,
        question,
        "Interactive post-simulation conversation.",
        use_mock=use_mock,
        model=model,
        memory_context=memory,
    )
    if db:
        db.store_agent_memory(agent.name, "conversation", response["message"], "CHAT")
    return response
