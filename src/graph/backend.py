from __future__ import annotations

from typing import Protocol

import networkx as nx


class PolicyGraphBackend(Protocol):
    def load_policy_graph(self, policy_text: str) -> nx.DiGraph:
        ...


class NetworkXPolicyGraphBackend:
    def load_policy_graph(self, policy_text: str) -> nx.DiGraph:
        from .typed_graph import build_typed_policy_graph

        return build_typed_policy_graph(policy_text)


class Neo4jPolicyGraphBackend:
    def __init__(self, database: str | None = None):
        from .neo4j_repository import Neo4jRepository

        self.repository = Neo4jRepository(database=database)

    def load_policy_graph(self, policy_text: str) -> nx.DiGraph:
        from .typed_graph import build_typed_policy_graph

        graph = build_typed_policy_graph(policy_text)
        self.repository.verify_connection()
        self.repository.ensure_schema()
        self.repository.upsert_graph(graph)
        return self.repository.read_graph()

    def close(self) -> None:
        self.repository.close()
