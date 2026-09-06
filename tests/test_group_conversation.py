from pathlib import Path

from src.data_layer.state_db import StateDatabase
from src.simulation.engine import run_simulation
from src.simulation.group_conversation import run_group_conversation


def test_group_conversation_routes_turns_over_graph(tmp_path: Path):
    result = run_simulation("Mandatory policy affects employees and clients.", days=1, employee_count=3)
    db = StateDatabase(tmp_path / "conversation.db")
    conversation = run_group_conversation(
        [*result.employees, *result.partners],
        result.graph,
        "How should we communicate the policy?",
        rounds=2,
        use_mock=True,
        db=db,
    )

    assert len(conversation.turns) > 0
    assert conversation.messages
    assert all(message.receiver in result.graph.nodes for message in conversation.messages)
    assert all(turn.sentiment in {"positive", "neutral", "negative", "mixed"} for turn in conversation.turns)
