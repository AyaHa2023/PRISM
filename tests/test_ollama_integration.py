from src.models.agents import Metrics, Personality, Role
from src.models.personas import AgentInternal
from src.simulation import llm_brain


def make_agent() -> AgentInternal:
    return AgentInternal(
        name="Amina",
        role=Role("Consultant", is_internal=True),
        personality=Personality("skeptical", "Questions implementation details.", 1.0),
        metrics=Metrics(stress=35, trust=80),
    )


def test_prompt_contains_ontology_graph_and_memory():
    prompt = llm_brain.generate_agent_prompt(
        make_agent(),
        "Mandatory return-to-office policy affects employees and clients.",
        "Manager says delivery pressure is rising.",
        graph_context="Policy (Policy) -> Clients (Stakeholder) [AFFECTS]",
        memory_context="Q2: Previous policy reaction increased stress.",
    )

    assert "Policy ontology" in prompt
    assert "Typed graph context" in prompt
    assert "Agent memory" in prompt
    assert "Previous policy reaction" in prompt
    assert "updated_stress" in prompt


def test_live_call_uses_client_and_normalizes_response(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, model, base_url):
            captured["model"] = model
            captured["base_url"] = base_url

        def structured_generate(self, prompt):
            captured["prompt"] = prompt
            return {"message": "I need clarification.", "updated_stress": 120, "updated_trust": -10}

    monkeypatch.setattr(llm_brain, "OllamaClient", FakeClient)
    result = llm_brain.call_llm(
        make_agent(),
        "Mandatory policy",
        use_mock=False,
        model="llama3.1:latest",
        graph_context="typed graph",
        memory_context="prior memory",
    )

    assert captured["model"] == "llama3.1:latest"
    assert captured["base_url"] == "http://localhost:11434"
    assert "typed graph" in captured["prompt"]
    assert result == {
        "message": "I need clarification.",
        "sentiment": "neutral",
        "updated_stress": 100,
        "updated_trust": 0,
    }
