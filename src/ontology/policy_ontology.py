from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PolicyOntology:
    policy_type: str = "unknown"
    severity: float = 0.0
    stakeholders: list[str] = field(default_factory=list)
    business_impact: str = "low"
    employee_impact: str = "low"
    external_trust_risk: str = "low"
    sentiment: str = "neutral"
    time_horizon: str = "short_term"
    risk_flags: list[str] = field(default_factory=list)
    raw_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


KEYWORD_MAP = {
    "return_to_office": {"policy_type": "return_to_office", "severity": 0.7},
    "rto": {"policy_type": "return_to_office", "severity": 0.7},
    "salary": {"policy_type": "salary_change", "severity": 0.6},
    "bonus": {"policy_type": "compensation_change", "severity": 0.4},
    "layoff": {"policy_type": "workforce_reduction", "severity": 0.9},
    "hybrid": {"policy_type": "work_model_change", "severity": 0.5},
    "remote": {"policy_type": "work_model_change", "severity": 0.5},
    "mandate": {"policy_type": "policy_change", "severity": 0.8},
    "mandatory": {"policy_type": "policy_change", "severity": 0.8},
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _detect_policy_type(raw_text: str) -> str:
    text = _normalize(raw_text)
    for key, cfg in KEYWORD_MAP.items():
        if key in text:
            return cfg["policy_type"]
    return "policy_change"


def _detect_severity(raw_text: str) -> float:
    text = _normalize(raw_text)
    score = 0.2
    if any(word in text for word in ["mandatory", "layoff", "cut", "reduce", "strict"]):
        score += 0.4
    if any(word in text for word in ["salary", "bonus", "return to office", "return-to-office", "hybrid", "remote"]):
        score += 0.2
    if any(word in text for word in ["support", "flexible", "clarification", "training"]):
        score -= 0.1
    return max(0.0, min(1.0, round(score, 2)))


def _detect_stakeholders(raw_text: str) -> list[str]:
    text = _normalize(raw_text)
    stakeholders: list[str] = []
    for label in ["employees", "managers", "hr", "clients", "partners", "consultants", "leadership", "team", "staff"]:
        if label in text:
            stakeholders.append(label)
    return sorted(set(stakeholders))


def _detect_sentiment(raw_text: str) -> str:
    text = _normalize(raw_text)
    negative = any(word in text for word in ["mandatory", "cut", "reduce", "strict", "risk", "penalty", "layoff"])
    positive = any(word in text for word in ["flexible", "support", "benefit", "clarification", "training"])
    if negative and not positive:
        return "negative"
    if positive and not negative:
        return "positive"
    return "neutral"


def extract_policy_ontology(raw_text: str) -> PolicyOntology:
    text = raw_text or ""
    policy_type = _detect_policy_type(text)
    severity = _detect_severity(text)
    stakeholders = _detect_stakeholders(text)
    sentiment = _detect_sentiment(text)

    business_impact = "high" if severity >= 0.7 else "medium" if severity >= 0.4 else "low"
    employee_impact = "high" if "employees" in " ".join(stakeholders) or severity >= 0.7 else "medium" if severity >= 0.4 else "low"
    external_trust_risk = "high" if "clients" in " ".join(stakeholders) or "partners" in " ".join(stakeholders) else "medium" if severity >= 0.6 else "low"

    flags: list[str] = []
    if "mandatory" in _normalize(text) or "strict" in _normalize(text):
        flags.append("mandatory_policy")
    if "salary" in _normalize(text) or "bonus" in _normalize(text):
        flags.append("compensation_change")
    if "return to office" in _normalize(text) or "return-to-office" in _normalize(text):
        flags.append("rto_policy")

    return PolicyOntology(
        policy_type=policy_type,
        severity=severity,
        stakeholders=stakeholders,
        business_impact=business_impact,
        employee_impact=employee_impact,
        external_trust_risk=external_trust_risk,
        sentiment=sentiment,
        time_horizon="short_term",
        risk_flags=flags,
        raw_summary=text[:300],
    )


def ontology_to_prompt(ontology: PolicyOntology) -> str:
    return json.dumps(ontology.to_dict(), indent=2)
