from __future__ import annotations

from itertools import product

import pandas as pd

from .engine import run_simulation
from .reporting import summarize_result


def repeated_scenario_runs(
    scenarios: list[dict],
    seeds: list[int],
    start_morale: int = 75,
    start_trust: int = 85,
    days: int = 10,
    employee_count: int = 5,
    use_mock_llm: bool = True,
    llm_model: str = "llama3.1:latest",
) -> pd.DataFrame:
    rows: list[dict] = []
    for scenario, seed in product(scenarios, seeds):
        result = run_simulation(
            scenario["policy"],
            start_morale=start_morale,
            start_trust=start_trust,
            days=days,
            employee_count=employee_count,
            use_mock_llm=use_mock_llm,
            llm_model=llm_model,
            random_seed=seed,
        )
        rows.append({
            "scenario_id": scenario.get("id", ""),
            "scenario": scenario.get("name", "Unnamed"),
            "seed": seed,
            "employee_count": employee_count,
            "days": days,
            **summarize_result(result),
        })
    return pd.DataFrame(rows)


def summarize_experiment(runs: pd.DataFrame) -> pd.DataFrame:
    if runs.empty:
        return pd.DataFrame()
    return (
        runs.groupby(["scenario_id", "scenario"], as_index=False)
        .agg(
            runs=("seed", "count"),
            average_stress=("average_stress", "mean"),
            stress_std=("average_stress", "std"),
            minimum_external_trust=("minimum_external_trust", "mean"),
            trust_std=("minimum_external_trust", "std"),
            leak_rate=("leak_count", lambda values: (values > 0).mean()),
        )
        .fillna(0.0)
        .round(3)
    )


def sensitivity_grid(
    policy_text: str,
    employee_counts: list[int],
    days_values: list[int],
    start_morale: int = 75,
    start_trust: int = 85,
) -> pd.DataFrame:
    rows: list[dict] = []
    for employee_count, days in product(employee_counts, days_values):
        result = run_simulation(
            policy_text,
            start_morale=start_morale,
            start_trust=start_trust,
            days=days,
            employee_count=employee_count,
            use_mock_llm=True,
            random_seed=42,
        )
        rows.append({
            "employee_count": employee_count,
            "days": days,
            **summarize_result(result),
            "network_density": result.network_metrics.get("density", 0.0),
        })
    return pd.DataFrame(rows)
