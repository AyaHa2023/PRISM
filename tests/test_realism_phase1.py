from src.ontology.llm_extractor import extract_policy_ontology_llm
from src.simulation.engine import run_simulation
from src.simulation.network_propagation import apply_neighbor_influence
from src.models.agents import Metrics, Personality, Role
from src.models.personas import AgentInternal
from src.simulation.message_bus import AgentMessage


def test_ontology_fallback_has_confidence_metadata():
    ontology, metadata = extract_policy_ontology_llm("Mandatory policy affects employees and clients.", use_mock=True)
    assert ontology.policy_type != "unknown"
    assert metadata["source"] == "deterministic"
    assert 0 <= metadata["confidence"] <= 1


def test_neighbor_influence_changes_metrics():
    agent = AgentInternal("B", Role("Consultant"), Personality("Pragmatic", "", 1.0), Metrics(stress=40, trust=70))
    messages = [AgentMessage(1, "A", "B", "informal", "bad news", "negative")]
    deltas = apply_neighbor_influence(agent, messages)
    assert deltas["stress_delta"] > 0
    assert agent.metrics.stress > 40


def test_simulation_exposes_ontology_and_message_propagation():
    result = run_simulation("Mandatory return-to-office affects employees and clients.", days=1, employee_count=3)
    assert result.policy_ontology is not None
    assert "confidence" in result.ontology_metadata
    assert result.messages
