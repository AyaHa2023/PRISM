from pathlib import Path

from src.graph.knowledge_graph import build_knowledge_graph, extract_policy_entities


TEXT = """
Mandatory return-to-office policy will affect employees, managers, and clients.
The HR team and partners are concerned about morale and trust.
This policy could increase stress and create a contract risk.
"""


def test_extract_policy_entities_finds_domain_terms():
    entities = extract_policy_entities(TEXT)
    labels = {item[0].lower() for item in entities}
    assert "employee" in labels or "employees" in labels
    assert "manager" in labels or "managers" in labels
    assert "hr" in labels or "human resources" in labels
    assert "client" in labels or "clients" in labels
    assert "policy" in labels


def test_build_knowledge_graph_creates_structured_edges():
    graph = build_knowledge_graph(TEXT)
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0
    edge_relations = {data.get("relation") for _, _, data in graph.edges(data=True)}
    assert "AFFECTS" in edge_relations or "RELATED_TO" in edge_relations
