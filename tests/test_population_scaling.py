from src.simulation.factory import generate_internal_employees
from src.simulation.engine import run_simulation


def test_factory_generates_requested_population():
    assert len(generate_internal_employees(count=10)) == 10
    assert len(generate_internal_employees(count=50)) == 50


def test_simulation_population_changes_network_size():
    small = run_simulation("Mandatory return-to-office affects employees.", days=1, employee_count=5)
    large = run_simulation("Mandatory return-to-office affects employees.", days=1, employee_count=20)
    assert len(small.employees) == 5
    assert len(large.employees) == 20
    assert large.network_metrics["node_count"] > small.network_metrics["node_count"]
