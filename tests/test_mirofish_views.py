from src.graph.scenario_visualization import scenario_graph_dot
from src.simulation.engine import run_simulation
from src.simulation.reporting import deterministic_report
from src.simulation.reporter_chat import ask_reporter


def test_scenario_graph_contains_policy_agents_and_message_edges():
    result = run_simulation("Mandatory policy affects employees and clients.", days=1, employee_count=3)
    dot = scenario_graph_dot(result)
    assert "digraph PrismScenario" in dot
    assert "Policy" in dot
    assert "agent_" in dot


def test_report_contains_mirofish_style_forecast_sections():
    result = run_simulation("Mandatory policy affects employees and clients.", days=1, employee_count=2)
    report = deterministic_report("Mandatory policy affects employees and clients.", result)
    assert report.narrative_paths
    assert report.turning_points
    assert report.confidence_gaps
    assert "confidence" in report.to_dict()


def test_reporter_chat_uses_report_without_llm():
    result = run_simulation("Mandatory policy affects employees and clients.", days=1, employee_count=2)
    report = deterministic_report("Mandatory policy affects employees and clients.", result)
    answer = ask_reporter("Why is this risky?", report, use_mock=True)
    assert "average stress" in answer
