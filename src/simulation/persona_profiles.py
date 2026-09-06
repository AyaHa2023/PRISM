from __future__ import annotations

import json
from typing import Any

from ..llm.ollama_client import OllamaClient
from ..models.personas import AgentBase

PROFILE_KEYS = {
    "communication_style",
    "decision_bias",
    "priorities",
    "concerns",
    "trust_behavior",
    "stress_sensitivity",
}


def default_profile(agent: AgentBase) -> dict[str, Any]:
    return {
        "communication_style": "direct and role-aware",
        "decision_bias": "pragmatic",
        "priorities": list(agent.role.priorities),
        "concerns": [agent.personality.description],
        "trust_behavior": "updates trust gradually from evidence",
        "stress_sensitivity": agent.personality.stress_sensitivity,
        "source": "factory",
    }


def _normalize_profile(payload: dict[str, Any], agent: AgentBase, source: str) -> dict[str, Any]:
    fallback = default_profile(agent)
    profile = {key: payload.get(key, fallback[key]) for key in PROFILE_KEYS}
    if not isinstance(profile["priorities"], list):
        profile["priorities"] = fallback["priorities"]
    if not isinstance(profile["concerns"], list):
        profile["concerns"] = fallback["concerns"]
    try:
        profile["stress_sensitivity"] = float(profile["stress_sensitivity"])
    except (TypeError, ValueError):
        profile["stress_sensitivity"] = fallback["stress_sensitivity"]
    profile["source"] = source
    return profile


def generate_persona_profile(
    agent: AgentBase,
    use_mock: bool = True,
    model: str = "llama3.1:latest",
) -> dict[str, Any]:
    fallback = default_profile(agent)
    if use_mock:
        return fallback
    prompt = f"""Create a concise workplace agent profile. Return JSON only.
Required keys: communication_style, decision_bias, priorities, concerns, trust_behavior, stress_sensitivity.
Agent name: {agent.name}
Role: {agent.role.title}
Role priorities: {agent.role.priorities}
Personality: {agent.personality.trait_name} - {agent.personality.description}
"""
    try:
        payload = OllamaClient(model=model).structured_generate(prompt, temperature=0.2)
        return _normalize_profile(payload, agent, "ollama")
    except Exception:
        return fallback


def profile_to_prompt(profile: dict[str, Any]) -> str:
    return json.dumps(profile, indent=2)
