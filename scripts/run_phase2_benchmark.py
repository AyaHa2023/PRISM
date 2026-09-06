from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.experiments import repeated_scenario_runs, sensitivity_grid, summarize_experiment
from src.simulation.mesa_scheduler import run_prism_population


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repeatability, sensitivity, and Mesa scale benchmarks.")
    parser.add_argument("--scenario-file", default="data/scenarios/scenarios_phase2.json")
    parser.add_argument("--days", type=int, default=5)
    parser.add_argument("--employees", type=int, default=10)
    args = parser.parse_args()

    scenarios = json.loads(Path(args.scenario_file).read_text(encoding="utf-8"))
    runs = repeated_scenario_runs(scenarios, seeds=[1, 2, 3], days=args.days, employee_count=args.employees)
    summary = summarize_experiment(runs)
    sensitivity = sensitivity_grid(
        "Mandatory return-to-office mandate with salary cut and strict delivery targets affects employees and clients.",
        employee_counts=[10, 50, 100],
        days_values=[3, 7, 14],
    )
    mesa = [run_prism_population(count, days=args.days).__dict__ for count in [10, 50, 100]]
    print(json.dumps({
        "repeat_runs": len(runs),
        "scenario_summary": summary.to_dict(orient="records"),
        "sensitivity": sensitivity.to_dict(orient="records"),
        "mesa_population": mesa,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
