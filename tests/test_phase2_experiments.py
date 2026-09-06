import json

from src.simulation.experiments import repeated_scenario_runs, sensitivity_grid, summarize_experiment
from src.simulation.mesa_scheduler import run_prism_population


def test_repeated_runs_are_repeatable_and_summarizable():
    scenarios = [{"id": "A", "name": "Baseline", "policy": "Flexible remote work with training."}]
    runs = repeated_scenario_runs(scenarios, seeds=[1, 2], days=1, employee_count=2)
    summary = summarize_experiment(runs)
    assert len(runs) == 2
    assert summary.iloc[0]["runs"] == 2
    assert "stress_std" in summary.columns


def test_sensitivity_grid_covers_population_and_time():
    grid = sensitivity_grid("Mandatory return-to-office affects employees.", [2, 4], [1, 3])
    assert len(grid) == 4
    assert set(grid["employee_count"]) == {2, 4}
    assert set(grid["days"]) == {1, 3}


def test_mesa_population_tracks_prism_metrics():
    result = run_prism_population(20, days=3)
    assert result.agent_count == 20
    assert result.average_stress > 25
    assert result.average_trust < 80
    assert len(result.ticks) == 3
