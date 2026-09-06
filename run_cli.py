#!/usr/bin/env python
"""CLI entry: run a simulation without Streamlit."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_layer.state_db import StateDatabase
from src.graph.knowledge_graph import build_knowledge_graph, load_seed_text
from src.simulation.engine import run_simulation

ROOT = Path(__file__).resolve().parent


def main() -> None:
    seed = load_seed_text(ROOT / "data" / "seed" / "policy_rto.txt")
    policy = "Mandatory return-to-office 4 days per week"
    print("=== Knowledge graph ===")
    kg = build_knowledge_graph(seed + "\n" + policy)
    print(f"Nodes: {kg.number_of_nodes()}, Edges: {kg.number_of_edges()}")

    print("\n=== 10-day simulation ===")
    db = StateDatabase(ROOT / "data" / "prism.db")
    result = run_simulation(policy, start_morale=70, start_trust=80, days=5, db=db)
    print(f"Events: {len(result.steps)}")
    for step in result.steps[:8]:
        print(f"  Day {step.day} [{step.quadrant}] {step.agent_name}: {step.message[:60]}…")
    print("\nDone. Open dashboard: streamlit run src/ui/app.py")


if __name__ == "__main__":
    main()
