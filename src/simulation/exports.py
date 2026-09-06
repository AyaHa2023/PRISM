from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def export_comparison_csv(comparison: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(path, index=False)
    return path


def export_comparison_json(comparison: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(comparison.to_dict(orient="records"), indent=2), encoding="utf-8")
    return path
