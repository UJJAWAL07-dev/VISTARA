"""
Configuration for the GIS Analysis Engine.

No hardcoded/machine-specific paths (matches /gis conventions).
Analysis-specific thresholds are centralized here so they're easy to
tune for the demo without hunting through multiple files.
"""

import os
from pathlib import Path


def _resolve_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


PROJECT_ROOT: Path = _resolve_project_root()
ANALYSIS_ROOT: Path = PROJECT_ROOT / "gis_analysis"

OUTPUT_ROOT: Path = Path(
    os.environ.get("VISTARA_ANALYSIS_OUTPUT_ROOT", ANALYSIS_ROOT / "_output")
)

# Minimum IoU for an AI-predicted feature to match ground truth.
IOU_MATCH_THRESHOLD = float(os.environ.get("VISTARA_IOU_MATCH_THRESHOLD", 0.5))

# Composite score weights. Components are normalized when optional inputs are absent.
SCORE_WEIGHTS = {
    "geometry_validity": 0.3,
    "shape_accuracy": 0.4,
    "ai_confidence": 0.3,
}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path