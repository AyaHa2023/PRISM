import json

from src.graph.network_metrics import calculate_network_metrics
from src.simulation.engine import run_simulation
from src.simulation.reporting import deterministic_report
from src.simulation.scenario_compare import compare_scenarios


def test_simulation_has_network_metrics_sentiment_and_report():
    result = run_simulation("Mandatory return-to-office affects employees and clients.", days=1, employee_count=2)
    report = deterministic_report("Mandatory return-to-office affects employees and clients.", result)

    assert result.network_metrics["node_count"] >= 2
    assert all(step.sentiment in {"positive", "neutral", "negative", "mixed"} for step in result.steps)
    assert report.to_dict()["key_risks"]
    json.dumps(report.to_dict())


def test_scenario_comparison_returns_comparable_rows():
    scenarios = [
        {"id": "A", "name": "Baseline", "policy": "Flexible remote work with training."},
        {"id": "B", "name": "Shock", "policy": "Mandatory return-to-office and salary cut."},
    ]
    comparison = compare_scenarios(scenarios, days=1, employee_count=2)

    assert list(comparison["scenario_id"]) == ["A", "B"]
    assert {"average_stress", "minimum_external_trust", "sentiment"}.issubset(comparison.columns)


def test_network_metrics_empty_graph():
    import networkx as nx

    assert calculate_network_metrics(nx.Graph())["node_count"] == 0
