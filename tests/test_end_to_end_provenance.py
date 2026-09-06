from src.simulation.engine import run_simulation


def test_simulation_records_backend_and_llm_provenance():
    result = run_simulation("Mandatory policy affects employees.", days=1, employee_count=2, use_mock_llm=True, graph_backend="networkx")
    assert result.graph_backend == "networkx"
    assert result.llm_model == "mock"
    assert result.policy_graph is not None
