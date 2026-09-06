from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Callable

from ..llm.ollama_client import OllamaClient
from ..ontology.policy_ontology import ontology_to_prompt
from .engine import SimulationResult
from .reporting import summarize_result


@dataclass
class SpecialistFinding:
    specialist: str
    finding: str
    sentiment: str
    risks: list[str]
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MultiAgentReport:
    findings: list[SpecialistFinding]
    synthesis: str
    overall_sentiment: str
    confidence: float

    def to_dict(self) -> dict:
        return {
            "findings": [finding.to_dict() for finding in self.findings],
            "synthesis": self.synthesis,
            "overall_sentiment": self.overall_sentiment,
            "confidence": self.confidence,
        }


SPECIALISTS = (
    ("employee_impact", "Assess employee stress, morale, trust, and adoption risk."),
    ("client_risk", "Assess client trust, delivery continuity, SLA, and external risk."),
    ("network_propagation", "Assess how the policy can spread through the supplied organizational network."),
)


def _fallback_finding(name: str, instruction: str, result: SimulationResult) -> SpecialistFinding:
    summary = summarize_result(result)
    if name == "employee_impact":
        finding = f"Average internal stress is {summary['average_stress']}/100."
        risks = ["stress escalation"] if summary["average_stress"] >= 60 else []
    elif name == "client_risk":
        finding = f"Minimum external trust is {summary['minimum_external_trust']}/100."
        risks = ["client trust erosion"] if summary["minimum_external_trust"] < 60 else []
    else:
        finding = f"The run produced {len(result.messages)} routed messages and {summary['leak_count']} external leaks."
        risks = ["network spillover"] if summary["leak_count"] else []
    return SpecialistFinding(name, finding, summary["sentiment"], risks, 0.4)


def run_multi_agent_report(
    result: SimulationResult,
    use_mock: bool = True,
    model: str = "llama3.1:latest",
    client_factory: Callable[..., OllamaClient] = OllamaClient,
) -> MultiAgentReport:
    findings: list[SpecialistFinding] = []
    for name, instruction in SPECIALISTS:
        fallback = _fallback_finding(name, instruction, result)
        if use_mock:
            findings.append(fallback)
            continue
        prompt = f"""You are the {name} specialist in Prism. {instruction}
Return JSON only with keys: finding, sentiment, risks, confidence.
Sentiment: positive, neutral, negative, or mixed. Confidence: 0 to 1.
Policy ontology: {ontology_to_prompt(result.policy_ontology) if result.policy_ontology else '{}'}
Simulation summary: {json.dumps(summarize_result(result))}
Network metrics: {json.dumps(result.network_metrics)}
"""
        try:
            payload = client_factory(model=model).structured_generate(prompt, temperature=0.2)
            sentiment = str(payload.get("sentiment", fallback.sentiment)).lower()
            if sentiment not in {"positive", "neutral", "negative", "mixed"}:
                sentiment = fallback.sentiment
            findings.append(
                SpecialistFinding(
                    name,
                    str(payload.get("finding", fallback.finding)),
                    sentiment,
                    [str(item) for item in payload.get("risks", fallback.risks)],
                    max(0.0, min(1.0, float(payload.get("confidence", fallback.confidence)))),
                )
            )
        except Exception:
            findings.append(fallback)

    negative = sum(f.sentiment == "negative" for f in findings)
    positive = sum(f.sentiment == "positive" for f in findings)
    overall = "negative" if negative > positive else "positive" if positive > negative else "mixed"
    risks = "; ".join(risk for finding in findings for risk in finding.risks) or "No specialist risk flag."
    synthesis = f"Specialists assessed the run as {overall}. Consolidated risks: {risks}"
    confidence = round(sum(f.confidence for f in findings) / len(findings), 3) if findings else 0.0
    return MultiAgentReport(findings, synthesis, overall, confidence)
