from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from ..llm.ollama_client import OllamaClient
from ..ontology.policy_ontology import extract_policy_ontology, ontology_to_prompt
from .engine import SimulationResult


@dataclass
class SimulationReport:
    headline: str
    executive_summary: str
    key_risks: list[str]
    recommended_actions: list[str]
    sentiment: str
    average_stress: float
    minimum_external_trust: float
    leak_count: int
    confidence: float
    narrative_paths: list[str] = field(default_factory=list)
    turning_points: list[str] = field(default_factory=list)
    confidence_gaps: list[str] = field(default_factory=list)
    source: str = "deterministic"

    def to_dict(self) -> dict:
        return asdict(self)


def summarize_result(result: SimulationResult) -> dict:
    internal = result.employees
    external = result.partners
    average_stress = round(sum(a.metrics.stress for a in internal) / len(internal), 1) if internal else 0.0
    minimum_trust = min((a.metrics.trust for a in external), default=0.0)
    sentiments = [step.sentiment for step in result.steps if step.sentiment]
    negative = sentiments.count("negative")
    positive = sentiments.count("positive")
    sentiment = "negative" if negative > positive else "positive" if positive > negative else "mixed"
    return {
        "average_stress": average_stress,
        "minimum_external_trust": minimum_trust,
        "leak_count": sum(step.event_type == "leak" for step in result.steps),
        "sentiment": sentiment,
    }


def deterministic_report(policy_text: str, result: SimulationResult) -> SimulationReport:
    ontology = extract_policy_ontology(policy_text)
    summary = summarize_result(result)
    risks: list[str] = []
    actions: list[str] = []
    if summary["average_stress"] >= 70:
        risks.append("Internal stress is high and may reduce delivery capacity.")
        actions.append("Use manager briefings and a staged rollout before full enforcement.")
    if summary["minimum_external_trust"] < 50:
        risks.append("External trust is below the escalation threshold.")
        actions.append("Prepare a client continuity plan and proactive account communication.")
    if summary["leak_count"]:
        risks.append("Internal pressure has propagated through an informal external channel.")
        actions.append("Give engagement leads an approved communication narrative.")
    if not risks:
        risks.append("No critical threshold was crossed in this run.")
        actions.append("Continue monitoring sentiment and trust over the next scenario window.")
    narrative_paths = [
        "Policy announcement -> employee interpretation -> neighbor discussion -> external risk review"
    ]
    turning_points = []
    if summary["average_stress"] >= 70:
        turning_points.append("Internal stress crossed the high-risk threshold.")
    if summary["leak_count"]:
        turning_points.append("An internal message crossed into the external channel.")
    if not turning_points:
        turning_points.append("No threshold crossing occurred in this simulation window.")
    confidence_gaps = [
        "Confidence is based on simulated reactions, not labelled organizational outcomes.",
        "The graph represents the configured topology and may omit undocumented relationships.",
    ]
    return SimulationReport(
        headline=f"{ontology.policy_type.replace('_', ' ').title()} risk assessment",
        executive_summary=(
            f"The simulation produced {summary['sentiment']} reactions with average internal stress "
            f"of {summary['average_stress']}/100 and minimum external trust of "
            f"{summary['minimum_external_trust']}/100."
        ),
        key_risks=risks,
        recommended_actions=actions,
        sentiment=summary["sentiment"],
        average_stress=summary["average_stress"],
        minimum_external_trust=summary["minimum_external_trust"],
        leak_count=summary["leak_count"],
        confidence=0.55,
        narrative_paths=narrative_paths,
        turning_points=turning_points,
        confidence_gaps=confidence_gaps,
    )


def generate_report(
    policy_text: str,
    result: SimulationResult,
    use_mock: bool = True,
    model: str = "llama3.1:latest",
) -> SimulationReport:
    fallback = deterministic_report(policy_text, result)
    if use_mock:
        return fallback
    ontology = extract_policy_ontology(policy_text)
    prompt = f"""You are the Prism report agent. Return valid JSON only.
Required keys: headline, executive_summary, key_risks, recommended_actions, sentiment, confidence, narrative_paths, turning_points, confidence_gaps.
Sentiment must be positive, neutral, negative, or mixed. Confidence must be between 0 and 1.
Policy ontology:
{ontology_to_prompt(ontology)}
Simulation summary:
{json.dumps(summarize_result(result), indent=2)}
Write an evidence-based executive report. Do not invent metrics outside the supplied summary.
"""
    try:
        payload = OllamaClient(model=model).structured_generate(prompt, temperature=0.2)
        return SimulationReport(
            headline=str(payload.get("headline", fallback.headline)),
            executive_summary=str(payload.get("executive_summary", fallback.executive_summary)),
            key_risks=[str(item) for item in payload.get("key_risks", fallback.key_risks)],
            recommended_actions=[str(item) for item in payload.get("recommended_actions", fallback.recommended_actions)],
            sentiment=str(payload.get("sentiment", fallback.sentiment)),
            average_stress=fallback.average_stress,
            minimum_external_trust=fallback.minimum_external_trust,
            leak_count=fallback.leak_count,
            confidence=max(0.0, min(1.0, float(payload.get("confidence", 0.7)))),
            narrative_paths=[str(item) for item in payload.get("narrative_paths", fallback.narrative_paths)],
            turning_points=[str(item) for item in payload.get("turning_points", fallback.turning_points)],
            confidence_gaps=[str(item) for item in payload.get("confidence_gaps", fallback.confidence_gaps)],
            source="ollama",
        )
    except Exception:
        return fallback
