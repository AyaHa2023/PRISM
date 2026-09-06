from __future__ import annotations

import networkx as nx

from ..models.personas import AgentBase
from .message_bus import AgentMessage


def apply_neighbor_influence(
    agent: AgentBase,
    messages: list[AgentMessage],
    influence_rate: float = 0.15,
) -> dict[str, int]:
    """Apply bounded social influence from messages received by one agent."""
    incoming = [message for message in messages if message.receiver == agent.name]
    if not incoming:
        return {"stress_delta": 0, "trust_delta": 0}
    negative = sum(message.sentiment == "negative" for message in incoming)
    positive = sum(message.sentiment == "positive" for message in incoming)
    stress_delta = round((negative - positive) * 8 * influence_rate)
    trust_delta = round((positive - negative) * 5 * influence_rate)
    agent.metrics.apply_delta(stress_delta=stress_delta, trust_delta=trust_delta)
    return {"stress_delta": stress_delta, "trust_delta": trust_delta}


def reachable_agents(graph: nx.Graph, source: str, hops: int = 2) -> set[str]:
    if source not in graph:
        return set()
    return set(nx.single_source_shortest_path_length(graph, source, cutoff=hops)) - {source}
