from __future__ import annotations

import pandas as pd

from ..data_layer.state_db import StateDatabase
from .engine import run_simulation
from .reporting import summarize_result


def compare_scenarios(
    scenarios: list[dict],
    start_morale: int = 75,
    start_trust: int = 85,
    days: int = 10,
    employee_count: int = 5,
    use_mock_llm: bool = True,
    llm_model: str = "llama3.1:latest",
    random_seed: int = 42,
) -> pd.DataFrame:
    rows: list[dict] = []
    for index, scenario in enumerate(scenarios):
        result = run_simulation(
            scenario["policy"],
            start_morale=start_morale,
            start_trust=start_trust,
            days=days,
            employee_count=employee_count,
            db=None,
            use_mock_llm=use_mock_llm,
            llm_model=llm_model,
            random_seed=random_seed + index,
        )
        metrics = summarize_result(result)
        rows.append({
            "scenario_id": scenario.get("id", ""),
            "scenario": scenario.get("name", "Unnamed"),
            "employee_count": employee_count,
            "days": days,
            "network_density": result.network_metrics.get("density", 0.0),
            **metrics,
        })
    return pd.DataFrame(rows)
