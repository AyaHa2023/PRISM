from pathlib import Path

from src.data_layer.state_db import StateDatabase
from src.simulation.scenario_generator import generate_policy_context
from src.simulation.engine import run_simulation
from src.ui.interactive_graph import graph_data_from_result


def test_mock_policy_generator_returns_concrete_scenario():
    scenario = generate_policy_context(use_mock=True)
    assert scenario["title"]
    assert len(scenario["policy"]) > 30
    assert scenario["stakeholders"]


def test_interactive_graph_data_contains_agents_and_edges():
    result = run_simulation("Mandatory policy affects employees and clients.", days=1, employee_count=2)
    graph_data = graph_data_from_result(result)
    assert graph_data["nodes"]
    assert graph_data["edges"]
    assert any(node["kind"] == "agent" for node in graph_data["nodes"])


def test_message_history_loads_from_sqlite(tmp_path: Path):
    db = StateDatabase(tmp_path / "state.db")
    result = run_simulation("Mandatory policy affects employees.", days=1, employee_count=2, db=db)
    history = db.load_messages()
    assert not history.empty
    assert "channel" in history.columns
