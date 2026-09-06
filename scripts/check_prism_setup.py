from __future__ import annotations

import importlib.util
import json
import os
import socket
import sys
from urllib.request import urlopen


def port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def ollama_ok() -> bool:
    try:
        with urlopen("http://localhost:11434/api/tags", timeout=3) as response:
            return response.status == 200
    except OSError:
        return False


result = {
    "python": sys.version.split()[0],
    "neo4j_bolt_open": port_open("127.0.0.1", 7687),
    "neo4j_browser_open": port_open("127.0.0.1", 7474),
    "ollama_reachable": ollama_ok(),
    "neo4j_password_configured": bool(os.getenv("NEO4J_PASSWORD")),
    "crew_ai_importable": importlib.util.find_spec("crewai") is not None,
    "database": os.getenv("NEO4J_DATABASE", "neo4j"),
}

print(json.dumps(result, indent=2))
missing = [
    name for name, ready in {
        "neo4j_bolt_open": result["neo4j_bolt_open"],
        "ollama_reachable": result["ollama_reachable"],
        "neo4j_password_configured": result["neo4j_password_configured"],
    }.items()
    if not ready
]
sys.exit(1 if missing else 0)
