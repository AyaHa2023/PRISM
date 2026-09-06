from __future__ import annotations

import os
from typing import Iterable

import networkx as nx

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - optional until Neo4j is installed
    GraphDatabase = None


class Neo4jRepository:
    """Optional Neo4j persistence adapter for the Prism graph schema."""

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        if GraphDatabase is None:
            raise RuntimeError("Install the optional neo4j package before using Neo4jRepository.")
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")
        if not self.password:
            raise ValueError("Set NEO4J_PASSWORD before connecting to Neo4j.")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def verify_connection(self) -> bool:
        try:
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1 AS ok").single()
        except Exception as error:
            raise RuntimeError(
                f"Cannot connect to Neo4j database '{self.database}' at '{self.uri}'. "
                "Start the PRISM DBMS, confirm Bolt is enabled on port 7687, "
                "and verify NEO4J_* credentials."
            ) from error
        return True

    def ensure_schema(self) -> None:
        statements = [
            "CREATE CONSTRAINT prism_node_name IF NOT EXISTS FOR (n:PrismNode) REQUIRE n.name IS UNIQUE",
            "CREATE INDEX prism_node_type IF NOT EXISTS FOR (n:PrismNode) ON (n.node_type)",
        ]
        with self.driver.session(database=self.database) as session:
            for statement in statements:
                session.run(statement).consume()

    def upsert_graph(self, graph: nx.Graph) -> int:
        query = """
        MERGE (source:PrismNode {name: $source})
        SET source.node_type = $source_type, source.label = $source_label
        MERGE (target:PrismNode {name: $target})
        SET target.node_type = $target_type, target.label = $target_label
        MERGE (source)-[edge:RELATES {relation: $relation}]->(target)
        SET edge.channel = $channel
        RETURN count(edge) AS count
        """
        rows = []
        for source, target, data in graph.edges(data=True):
            rows.append(
                {
                    "source": source,
                    "source_type": graph.nodes[source].get("node_type", "Unknown"),
                    "source_label": graph.nodes[source].get("label", source),
                    "target": target,
                    "target_type": graph.nodes[target].get("node_type", "Unknown"),
                    "target_label": graph.nodes[target].get("label", target),
                    "relation": data.get("relation", "RELATED_TO"),
                    "channel": data.get("channel", "semantic"),
                }
            )
        with self.driver.session(database=self.database) as session:
            for row in rows:
                session.run(query, **row).consume()
        return len(rows)

    def read_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        query = """
        MATCH (source:PrismNode)-[edge:RELATES]->(target:PrismNode)
        RETURN source, target, edge
        """
        with self.driver.session(database=self.database) as session:
            for record in session.run(query):
                source = dict(record["source"])
                target = dict(record["target"])
                edge = dict(record["edge"])
                graph.add_node(source["name"], **source)
                graph.add_node(target["name"], **target)
                graph.add_edge(source["name"], target["name"], **edge)
        return graph

    def read_neighborhood(self, node_name: str, limit: int = 20) -> list[dict]:
        query = """
        MATCH (source:PrismNode {name: $name})-[edge:RELATES]->(target:PrismNode)
        RETURN target.name AS name, target.node_type AS node_type, edge.relation AS relation
        LIMIT $limit
        """
        with self.driver.session(database=self.database) as session:
            return [dict(record) for record in session.run(query, name=node_name, limit=limit)]

    def close(self) -> None:
        self.driver.close()

    def __enter__(self) -> "Neo4jRepository":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
