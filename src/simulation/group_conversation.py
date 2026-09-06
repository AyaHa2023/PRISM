from __future__ import annotations

from dataclasses import asdict, dataclass

import networkx as nx

from ..data_layer.state_db import StateDatabase
from ..models.personas import AgentBase
from .llm_brain import call_llm
from .message_bus import AgentMessage, route_to_neighbors
from .persona_profiles import profile_to_prompt


@dataclass
class ConversationTurn:
    round_number: int
    speaker: str
    channel: str
    message: str
    sentiment: str
    stress: int
    trust: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GroupConversation:
    topic: str
    turns: list[ConversationTurn]
    messages: list[AgentMessage]

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "turns": [turn.to_dict() for turn in self.turns],
            "messages": [message.to_dict() for message in self.messages],
        }


def run_group_conversation(
    agents: list[AgentBase],
    graph: nx.Graph,
    topic: str,
    rounds: int = 2,
    use_mock: bool = True,
    model: str = "llama3.1:latest",
    db: StateDatabase | None = None,
) -> GroupConversation:
    """Run a bounded employee/partner conversation over actual graph edges."""
    agent_by_name = {agent.name: agent for agent in agents}
    turns: list[ConversationTurn] = []
    messages: list[AgentMessage] = []
    pending: list[AgentMessage] = []

    for round_number in range(1, max(1, rounds) + 1):
        for agent in agents:
            if agent.name not in graph:
                continue
            incoming = [message for message in pending if message.receiver == agent.name]
            neighbor_context = "; ".join(
                f"{message.sender}: {message.text}" for message in incoming
            ) or "No neighbor response yet."
            context = (
                f"Group conversation round {round_number}. Topic: {topic}. "
                f"Messages received through connected relationships: {neighbor_context}"
            )
            response = call_llm(
                agent,
                topic,
                context,
                use_mock=use_mock,
                model=model,
                memory_context=db.build_agent_context(agent.name) if db else "",
                profile_context=profile_to_prompt(agent.profile),
            )
            neighbors = route_to_neighbors(
                graph,
                round_number,
                agent.name,
                response["message"],
                response.get("sentiment", "neutral"),
                channel="group_conversation",
            )
            pending.extend(neighbors)
            messages.extend(neighbors)
            if db:
                db.store_agent_memory(agent.name, "group_conversation", response["message"], "GROUP")
                for message in neighbors:
                    db.store_message(message.to_dict())
            turns.append(
                ConversationTurn(
                    round_number=round_number,
                    speaker=agent.name,
                    channel="group_conversation",
                    message=response["message"],
                    sentiment=response.get("sentiment", "neutral"),
                    stress=agent.metrics.stress,
                    trust=agent.metrics.trust,
                )
            )

    return GroupConversation(topic=topic, turns=turns, messages=messages)
