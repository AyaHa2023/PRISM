from pathlib import Path

from src.graph.backend import NetworkXPolicyGraphBackend
from src.simulation.engine import run_simulation
from src.simulation.mesa_scheduler import validate_population_scale
from src.simulation.multi_agent_workflow import run_multi_agent_report
from src.simulation.outcome_evaluation import LabelledOutcome, evaluate_predictions, evaluate_scenario


def test_backend_interface_builds_networkx_graph():
    graph = NetworkXPolicyGraphBackend().load_policy_graph("Mandatory policy affects employees.")
    assert graph.has_edge("Policy", "Employees")


def test_multi_agent_workflow_has_specialist_findings():
    result = run_simulation("Mandatory policy affects employees and clients.", days=1, employee_count=2)
    report = run_multi_agent_report(result, use_mock=True)
    assert len(report.findings) == 3
    assert report.overall_sentiment in {"positive", "neutral", "negative", "mixed"}


def test_labelled_outcome_evaluation():
    result = run_simulation("Mandatory policy affects employees and clients.", days=1, employee_count=2)
    evaluation = evaluate_scenario(
        "C",
        result,
        LabelledOutcome("C", 40, 70, "mixed"),
    )
    calibration = evaluate_predictions([evaluation])
    assert calibration.sample_count == 1
    assert evaluation.stress_error >= 0


def test_mesa_population_scale():
    runs = validate_population_scale([10, 100], days=2)
    assert [run.agent_count for run in runs] == [10, 100]
    assert all(len(run.ticks) == 2 for run in runs)
