from pathlib import Path

import pandas as pd

from src.simulation.calibration import calibrate_predictions
from src.simulation.exports import export_comparison_csv, export_comparison_json


def test_calibration_returns_error_and_accuracy_metrics():
    result = calibrate_predictions(
        [{"stress": 60, "trust": 70, "sentiment": "negative"}],
        [{"stress": 65, "trust": 80, "sentiment": "negative"}],
    )
    assert result.sample_count == 1
    assert result.stress_mae == 5.0
    assert result.trust_mae == 10.0
    assert result.sentiment_accuracy == 1.0


def test_exports_write_comparison_files(tmp_path: Path):
    frame = pd.DataFrame([{"scenario": "A", "average_stress": 50}])
    assert export_comparison_csv(frame, tmp_path / "comparison.csv").exists()
    assert export_comparison_json(frame, tmp_path / "comparison.json").exists()
