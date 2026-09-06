from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.graph.neo4j_repository import Neo4jRepository
from src.graph.typed_graph import build_typed_policy_graph


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate one Prism policy graph into Neo4j.")
    parser.add_argument(
        "--policy",
        default="Mandatory return-to-office policy affects employees and clients.",
        help="Policy text used to build the typed graph.",
    )
    parser.add_argument("--database", default="prismDB", help="Neo4j database name.")
    args = parser.parse_args()

    graph = build_typed_policy_graph(args.policy)
    with Neo4jRepository(database=args.database) as repository:
        repository.verify_connection()
        repository.ensure_schema()
        edge_count = repository.upsert_graph(graph)

    print(
        json.dumps(
            {
                "ok": True,
                "database": args.database,
                "nodes": graph.number_of_nodes(),
                "edges_written": edge_count,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
