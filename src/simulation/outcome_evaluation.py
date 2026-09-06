from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .calibration import CalibrationResult, calibrate_predictions
from .engine import SimulationResult
from .reporting import summarize_result


@dataclass
class LabelledOutcome:
    scenario_id: str
    expected_stress: float
    expected_trust: float
    expected_sentiment: str


@dataclass
class ScenarioEvaluation:
    scenario_id: str
    predicted_stress: float
    predicted_trust: float
    predicted_sentiment: str
    expected_stress: float
    expected_trust: float
    expected_sentiment: str
    stress_error: float
    trust_error: float
    sentiment_correct: bool

    def to_dict(self) -> dict:
        return asdict(self)


def load_labelled_outcomes(path: Path) -> list[LabelledOutcome]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [LabelledOutcome(**row) for row in data]


def evaluate_scenario(scenario_id: str, result: SimulationResult, outcome: LabelledOutcome) -> ScenarioEvaluation:
    summary = summarize_result(result)
    return ScenarioEvaluation(
        scenario_id=scenario_id,
        predicted_stress=summary["average_stress"],
        predicted_trust=summary["minimum_external_trust"],
        predicted_sentiment=summary["sentiment"],
        expected_stress=outcome.expected_stress,
        expected_trust=outcome.expected_trust,
        expected_sentiment=outcome.expected_sentiment,
        stress_error=round(abs(summary["average_stress"] - outcome.expected_stress), 3),
        trust_error=round(abs(summary["minimum_external_trust"] - outcome.expected_trust), 3),
        sentiment_correct=summary["sentiment"] == outcome.expected_sentiment,
    )


def evaluate_predictions(evaluations: list[ScenarioEvaluation]) -> CalibrationResult:
    return calibrate_predictions(
        [
            {"stress": item.predicted_stress, "trust": item.predicted_trust, "sentiment": item.predicted_sentiment}
            for item in evaluations
        ],
        [
            {"stress": item.expected_stress, "trust": item.expected_trust, "sentiment": item.expected_sentiment}
            for item in evaluations
        ],
    )
