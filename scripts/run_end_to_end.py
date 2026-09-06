from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation.engine import run_simulation
from src.simulation.reporting import generate_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Prism simulation through Neo4j and Ollama.")
    parser.add_argument("--database", default="prismDB")
    parser.add_argument("--model", default="llama3.1:latest")
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--employees", type=int, default=2)
    parser.add_argument("--policy", default="Mandatory return-to-office policy affects employees and clients.")
    args = parser.parse_args()

    result = run_simulation(
        args.policy,
        days=args.days,
        employee_count=args.employees,
        use_mock_llm=False,
        llm_model=args.model,
        graph_backend="neo4j",
        graph_database=args.database,
    )
    report = generate_report(args.policy, result, use_mock=False, model=args.model)
    output = {
        "ok": True,
        "graph_backend": result.graph_backend,
        "graph_nodes": result.policy_graph.number_of_nodes() if result.policy_graph else 0,
        "graph_edges": result.policy_graph.number_of_edges() if result.policy_graph else 0,
        "ontology_source": result.ontology_metadata.get("source"),
        "ontology_confidence": result.ontology_metadata.get("confidence"),
        "llm_model": result.llm_model,
        "agent_events": len(result.steps),
        "message_count": len(result.messages),
        "report_source": report.source,
        "report_sentiment": report.sentiment,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
