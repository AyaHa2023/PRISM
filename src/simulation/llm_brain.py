"""Step 3 — agent 'brain' with mock rules + optional local Ollama hook."""

from __future__ import annotations

import json
import os
import random
import re

from ..llm.ollama_client import OllamaClient
from ..graph.typed_graph import build_typed_policy_graph, summarize_typed_graph
from ..models.personas import AgentBase
from ..ontology.policy_ontology import extract_policy_ontology, ontology_to_prompt
from .persona_profiles import profile_to_prompt


NEGATIVE_KEYWORDS = [
    "cut", "reduce", "mandatory", "mandate", "layoff", "penalty", "strict", "10%", "outsourc"
]
POSITIVE_KEYWORDS = ["bonus", "flexible", "remote", "support", "training", "clarification"]


def generate_agent_prompt(
    agent: AgentBase,
    event: str,
    context_messages: str,
    graph_context: str = "",
    memory_context: str = "",
    profile_context: str = "",
) -> str:
    side = "Internal" if agent.role.is_internal else "External"
    ontology = extract_policy_ontology(event)
    graph_context = graph_context or summarize_typed_graph(build_typed_policy_graph(event))
    return f"""You are {agent.name}, {side} {agent.role.title}.
Personality: {agent.personality.trait_name} — {agent.personality.description}
Stress={agent.metrics.stress}/100, Trust={agent.metrics.trust}/100
Context: {context_messages}
Agent memory: {memory_context or 'No prior memory.'}
Agent profile: {profile_context or profile_to_prompt(agent.profile)}
Typed graph context: {graph_context}
Policy ontology: {ontology_to_prompt(ontology)}
Event: {event}
Return valid JSON only with exactly these keys: message, sentiment, updated_stress, updated_trust.
Sentiment must be one of: positive, neutral, negative, mixed.
Keep updated_stress and updated_trust as integers from 0 to 100.
Keep the response brief and realistic for a workplace scenario.
"""


def _score_event(event: str) -> int:
    lower = event.lower()
    score = 0
    for w in NEGATIVE_KEYWORDS:
        if w in lower:
            score -= 8
    for w in POSITIVE_KEYWORDS:
        if w in lower:
            score += 5
    return score


def mock_llm_response(agent: AgentBase, event: str, context_messages: str = "") -> dict:
    """
    Student-friendly mock: no API key.
    Uses personality sensitivity + keyword heuristics (ABM rule layer).
    """
    event_score = _score_event(event)
    sensitivity = agent.personality.stress_sensitivity

    stress_delta = int(-event_score * 0.6 * sensitivity)
    trust_delta = int(event_score * 0.4)

    if "chaotic" in context_messages.lower() or "frustration" in context_messages.lower():
        stress_delta += random.randint(3, 8)

    new_stress = agent.metrics.stress + stress_delta
    new_trust = agent.metrics.trust + trust_delta

    trait = agent.personality.trait_name.lower()
    if "skeptical" in trait:
        new_trust -= 5
        tone = "I'm not convinced this will work."
    elif "conflict-averse" in trait:
        new_stress += 5
        tone = "I'll stay quiet, but this adds pressure."
    else:
        tone = "We need more detail before judging."

    if event_score < -10:
        message = f"{tone} The policy feels heavy-handed for our team."
        sentiment = "negative"
    elif event_score > 5:
        message = f"{tone} This could help if communicated clearly."
        sentiment = "positive"
    else:
        message = f"{tone} Waiting to see how managers implement it."
        sentiment = "mixed"

    return {
        "message": message,
        "sentiment": sentiment,
        "updated_stress": max(0, min(100, new_stress)),
        "updated_trust": max(0, min(100, new_trust)),
    }


def call_llm(
    agent: AgentBase,
    event: str,
    context_messages: str = "",
    use_mock: bool = True,
    model: str = "llama3.1:latest",
    graph_context: str = "",
    memory_context: str = "",
    profile_context: str = "",
) -> dict:
    if use_mock:
        return mock_llm_response(agent, event, context_messages)

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    client = OllamaClient(model=model, base_url=ollama_url)
    prompt = generate_agent_prompt(agent, event, context_messages, graph_context, memory_context, profile_context)

    try:
        payload = client.structured_generate(prompt)
    except Exception:
        return mock_llm_response(agent, event, context_messages)

    message = payload.get("message") if isinstance(payload, dict) else None
    if not message:
        return mock_llm_response(agent, event, context_messages)

    stress = int(payload.get("updated_stress", agent.metrics.stress))
    trust = int(payload.get("updated_trust", agent.metrics.trust))
    sentiment = str(payload.get("sentiment", "neutral")).lower()
    if sentiment not in {"positive", "neutral", "negative", "mixed"}:
        sentiment = "neutral"
    return {
        "message": str(message),
        "sentiment": sentiment,
        "updated_stress": max(0, min(100, stress)),
        "updated_trust": max(0, min(100, trust)),
    }


def parse_llm_json(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    return None
