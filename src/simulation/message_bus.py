from __future__ import annotations

from dataclasses import asdict, dataclass

import networkx as nx


@dataclass
class AgentMessage:
    day: int
    sender: str
    receiver: str
    channel: str
    text: str
    sentiment: str
    stress_delta: int = 0
    trust_delta: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def route_to_neighbors(
    graph: nx.Graph,
    day: int,
    sender: str,
    text: str,
    sentiment: str,
    channel: str = "informal",
) -> list[AgentMessage]:
    messages: list[AgentMessage] = []
    for receiver in graph.neighbors(sender):
        edge = graph.get_edge_data(sender, receiver) or {}
        messages.append(
            AgentMessage(
                day=day,
                sender=sender,
                receiver=receiver,
                channel=edge.get("channel", channel),
                text=text,
                sentiment=sentiment,
            )
        )
    return messages
