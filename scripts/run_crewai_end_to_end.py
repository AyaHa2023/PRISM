from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.crewai_workflow import run_crewai_review
from src.simulation.engine import run_simulation
from src.simulation.reporting import generate_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Prism through Neo4j, Ollama, and CrewAI.")
    parser.add_argument("--database", default="prismDB")
    parser.add_argument("--model", default="llama3.1:latest")
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--employees", type=int, default=2)
    args = parser.parse_args()

    result = run_simulation(
        "Mandatory return-to-office policy affects employees and clients.",
        days=args.days,
        employee_count=args.employees,
        use_mock_llm=False,
        llm_model=args.model,
        graph_backend="neo4j",
        graph_database=args.database,
    )
    report = generate_report(
        "Mandatory return-to-office policy affects employees and clients.",
        result,
        use_mock=False,
        model=args.model,
    )
    crew_report = run_crewai_review(result, model=f"ollama/{args.model}")
    print(json.dumps({
        "ok": True,
        "graph_backend": result.graph_backend,
        "graph_nodes": result.policy_graph.number_of_nodes() if result.policy_graph else 0,
        "graph_edges": result.policy_graph.number_of_edges() if result.policy_graph else 0,
        "ontology_source": result.ontology_metadata.get("source"),
        "reaction_model": result.llm_model,
        "report_source": report.source,
        "crewai_source": crew_report.get("source"),
        "crewai_result_present": bool(crew_report.get("result")),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
