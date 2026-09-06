from __future__ import annotations

from typing import Any

from ..llm.ollama_client import OllamaClient
from .policy_ontology import PolicyOntology, extract_policy_ontology


def _validated_payload(payload: dict[str, Any], fallback: PolicyOntology) -> dict[str, Any]:
    allowed_sentiments = {"positive", "neutral", "negative", "mixed"}
    sentiment = str(payload.get("sentiment", fallback.sentiment)).lower()
    if sentiment not in allowed_sentiments:
        sentiment = fallback.sentiment
    try:
        severity = max(0.0, min(1.0, float(payload.get("severity", fallback.severity))))
    except (TypeError, ValueError):
        severity = fallback.severity
    stakeholders = payload.get("stakeholders", fallback.stakeholders)
    if not isinstance(stakeholders, list):
        stakeholders = fallback.stakeholders
    evidence = payload.get("evidence", [])
    if not isinstance(evidence, list):
        evidence = []
    relations = payload.get("relations", [])
    if not isinstance(relations, list):
        relations = []
    try:
        confidence = max(0.0, min(1.0, float(payload.get("confidence", 0.5))))
    except (TypeError, ValueError):
        confidence = 0.5
    return {
        "policy_type": str(payload.get("policy_type", fallback.policy_type)),
        "severity": severity,
        "stakeholders": [str(item) for item in stakeholders],
        "business_impact": str(payload.get("business_impact", fallback.business_impact)),
        "employee_impact": str(payload.get("employee_impact", fallback.employee_impact)),
        "external_trust_risk": str(payload.get("external_trust_risk", fallback.external_trust_risk)),
        "sentiment": sentiment,
        "time_horizon": str(payload.get("time_horizon", fallback.time_horizon)),
        "risk_flags": [str(item) for item in payload.get("risk_flags", fallback.risk_flags)],
        "evidence": evidence,
        "relations": relations,
        "confidence": confidence,
    }


def extract_policy_ontology_llm(
    text: str,
    use_mock: bool = True,
    model: str = "llama3.1:latest",
) -> tuple[PolicyOntology, dict[str, Any]]:
    fallback = extract_policy_ontology(text)
    if use_mock:
        return fallback, {
            "source": "deterministic",
            "confidence": 0.45,
            "evidence": [],
            "relations": [],
        }
    prompt = f"""Extract a workplace policy ontology. Return valid JSON only.
Required keys: policy_type, severity, stakeholders, business_impact, employee_impact,
external_trust_risk, sentiment, time_horizon, risk_flags, evidence, relations, confidence.
Evidence items must contain: text, entity, entity_type.
Relation items must contain: source, relation, target, evidence.
Confidence must be between 0 and 1. Do not invent entities not supported by the text.
Policy text: {text}
"""
    try:
        payload = OllamaClient(model=model).structured_generate(prompt, temperature=0.0)
        validated = _validated_payload(payload, fallback)
        ontology = PolicyOntology(
            policy_type=validated["policy_type"], severity=validated["severity"],
            stakeholders=validated["stakeholders"], business_impact=validated["business_impact"],
            employee_impact=validated["employee_impact"], external_trust_risk=validated["external_trust_risk"],
            sentiment=validated["sentiment"], time_horizon=validated["time_horizon"],
            risk_flags=validated["risk_flags"], raw_summary=text[:300],
        )
        metadata = {"source": "ollama", "confidence": validated["confidence"], "evidence": validated["evidence"], "relations": validated["relations"]}
        return ontology, metadata
    except Exception:
        return fallback, {"source": "deterministic_fallback", "confidence": 0.35, "evidence": [], "relations": []}
