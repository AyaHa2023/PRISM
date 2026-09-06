from pathlib import Path

from src.data_layer.state_db import StateDatabase
from src.models.agents import Metrics, Personality, Role
from src.models.personas import AgentInternal
from src.simulation.engine import run_simulation
from src.simulation.message_bus import route_to_neighbors
from src.simulation.persona_profiles import generate_persona_profile


def test_profile_fallback_is_structured():
    agent = AgentInternal("Amina", Role("Consultant"), Personality("Pragmatic", "Looks for compromises"), Metrics())
    profile = generate_persona_profile(agent, use_mock=True)
    assert profile["source"] == "factory"
    assert profile["priorities"] == []
    assert isinstance(profile["concerns"], list)


def test_message_bus_only_routes_to_neighbors():
    import networkx as nx

    graph = nx.Graph()
    graph.add_edge("A", "B", channel="informal")
    messages = route_to_neighbors(graph, 1, "A", "hello", "neutral")
    assert len(messages) == 1
    assert messages[0].receiver == "B"


def test_simulation_persists_profiles_and_messages(tmp_path: Path):
    db = StateDatabase(tmp_path / "state.db")
    result = run_simulation("Mandatory return-to-office affects employees and clients.", days=1, employee_count=2, db=db)
    assert result.employees[0].profile
    assert db.load_agent_profile(result.employees[0].name)
    assert isinstance(result.messages, list)
