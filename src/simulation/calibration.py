from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CalibrationResult:
    sample_count: int
    stress_mae: float
    trust_mae: float
    sentiment_accuracy: float


def calibrate_predictions(predictions: list[dict], outcomes: list[dict]) -> CalibrationResult:
    if len(predictions) != len(outcomes):
        raise ValueError("Predictions and outcomes must have the same length.")
    if not predictions:
        return CalibrationResult(0, 0.0, 0.0, 0.0)

    stress_errors = [abs(float(p["stress"]) - float(o["stress"])) for p, o in zip(predictions, outcomes)]
    trust_errors = [abs(float(p["trust"]) - float(o["trust"])) for p, o in zip(predictions, outcomes)]
    sentiment_hits = [p.get("sentiment") == o.get("sentiment") for p, o in zip(predictions, outcomes)]
    return CalibrationResult(
        sample_count=len(predictions),
        stress_mae=round(sum(stress_errors) / len(stress_errors), 3),
        trust_mae=round(sum(trust_errors) / len(trust_errors), 3),
        sentiment_accuracy=round(sum(sentiment_hits) / len(sentiment_hits), 3),
    )
