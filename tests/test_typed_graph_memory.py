from pathlib import Path

from src.data_layer.state_db import StateDatabase
from src.graph.typed_graph import build_typed_policy_graph, summarize_typed_graph


def test_typed_graph_builds_policy_and_stakeholder_nodes():
    graph = build_typed_policy_graph("Mandatory return-to-office policy affects employees, managers, and clients.")

    assert "Policy" in graph.nodes
    assert graph.nodes["Policy"]["node_type"] == "Policy"
    assert "Employees" in graph.nodes
    assert "Clients" in graph.nodes
    assert any(data.get("relation") == "AFFECTS" for _, _, data in graph.edges(data=True))


def test_agent_memory_round_trip(tmp_path: Path):
    db = StateDatabase(tmp_path / "memory.db")
    assert db.get_agent_memory("Amina") == []
    assert "no stored memory" in db.build_agent_context("Amina")
    db.store_agent_memory("Amina", "reaction", "Stress increased after memo", "Q2")
    row = db.get_agent_memory("Amina", limit=5)[0]

    assert row["agent_name"] == "Amina"
    assert "Stress increased" in row["summary"]
    assert db.build_agent_context("Amina", limit=5) != ""


def test_graph_summary_contains_context_for_prompting():
    summary = summarize_typed_graph(build_typed_policy_graph("Salary cut and mandatory policy create client trust risk."))
    assert "Policy" in summary or "salary" in summary.lower()
    assert "risk" in summary.lower()
