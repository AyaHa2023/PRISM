import networkx as nx
import pytest

from src.graph import neo4j_repository


def test_neo4j_repository_requires_optional_driver(monkeypatch):
    monkeypatch.setattr(neo4j_repository, "GraphDatabase", None)
    with pytest.raises(RuntimeError, match="optional neo4j package"):
        neo4j_repository.Neo4jRepository(password="test")


def test_typed_graph_is_directed_for_migration():
    from src.graph.typed_graph import build_typed_policy_graph

    graph = build_typed_policy_graph("Mandatory policy affects employees and clients.")
    assert isinstance(graph, nx.DiGraph)
    assert graph.has_edge("Policy", "Employees")


def test_neo4j_repository_reads_database_from_environment(monkeypatch):
    class FakeDriver:
        pass

    class FakeGraphDatabase:
        @staticmethod
        def driver(uri, auth):
            return FakeDriver()

    monkeypatch.setattr(neo4j_repository, "GraphDatabase", FakeGraphDatabase)
    monkeypatch.setenv("NEO4J_DATABASE", "prismDB")
    repository = neo4j_repository.Neo4jRepository(password="test")

    assert repository.database == "prismDB"


def test_connection_error_is_actionable(monkeypatch):
    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def run(self, _query):
            raise ConnectionError("connection refused")

    class FakeDriver:
        def session(self, database):
            assert database == "prismDB"
            return FakeSession()

    class FakeGraphDatabase:
        @staticmethod
        def driver(uri, auth):
            return FakeDriver()

    monkeypatch.setattr(neo4j_repository, "GraphDatabase", FakeGraphDatabase)
    repository = neo4j_repository.Neo4jRepository(password="test", database="prismDB")

    with pytest.raises(RuntimeError, match="Start the PRISM DBMS"):
        repository.verify_connection()
