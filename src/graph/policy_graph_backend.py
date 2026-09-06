from __future__ import annotations

import networkx as nx

from .backend import Neo4jPolicyGraphBackend, NetworkXPolicyGraphBackend


def build_policy_graph(policy_text: str, backend: str = "networkx", database: str | None = None) -> nx.DiGraph:
    if backend == "networkx":
        return NetworkXPolicyGraphBackend().load_policy_graph(policy_text)
    if backend != "neo4j":
        raise ValueError(f"Unsupported graph backend: {backend}")
    adapter = Neo4jPolicyGraphBackend(database=database)
    try:
        return adapter.load_policy_graph(policy_text)
    finally:
        adapter.close()
