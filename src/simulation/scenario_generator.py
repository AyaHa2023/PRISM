from __future__ import annotations

import json
from typing import Any

from ..llm.ollama_client import OllamaClient


def generate_policy_context(use_mock: bool = False, model: str = "llama3.1:latest") -> dict[str, Any]:
    fallback = {
        "title": "Staged hybrid delivery policy",
        "policy": "Introduce a staged hybrid schedule with manager training, transport support, and a six-week review.",
        "context": "A professional-services organization is balancing delivery continuity, employee flexibility, and client trust.",
        "stakeholders": ["employees", "managers", "clients", "partners"],
        "risks": ["manager coordination", "uneven adoption", "client continuity"],
    }
    if use_mock:
        return fallback
    prompt = """Generate one realistic workplace policy scenario for a professional-services organization.
Return JSON only with keys: title, policy, context, stakeholders, risks.
The policy must contain concrete actors, a measurable change, a time horizon, and an operational tradeoff.
Avoid generic AI language. Make it plausible for a PwC-like organization and client ecosystem.
"""
    try:
        payload = OllamaClient(model=model).structured_generate(prompt, temperature=0.8)
        if not payload.get("policy") or not payload.get("title"):
            return fallback
        return {
            "title": str(payload["title"]),
            "policy": str(payload["policy"]),
            "context": str(payload.get("context", "")),
            "stakeholders": [str(item) for item in payload.get("stakeholders", [])],
            "risks": [str(item) for item in payload.get("risks", [])],
        }
    except Exception:
        return fallback


def policy_context_text(context: dict[str, Any]) -> str:
    return json.dumps(context, indent=2)
