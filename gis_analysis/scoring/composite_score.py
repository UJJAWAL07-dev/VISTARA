"""Composite quality/confidence scoring for AI-predicted features."""

import math
from typing import Any, Dict, List, Optional

from gis_analysis.config import SCORE_WEIGHTS
from gis_analysis.exceptions import ScoringError

DEFAULT_AI_CONFIDENCE = 0.5
_COMPONENTS = ("geometry_validity", "shape_accuracy", "ai_confidence")


def _resolve_weights(weights: Optional[Dict[str, float]]) -> Dict[str, float]:
    resolved = dict(SCORE_WEIGHTS if weights is None else weights)
    missing = [component for component in _COMPONENTS if component not in resolved]
    if missing:
        raise ScoringError(f"score weights missing components: {missing}")
    try:
        total = sum(float(resolved[component]) for component in _COMPONENTS)
    except (TypeError, ValueError) as error:
        raise ScoringError(f"score weights must be numeric: {resolved}") from error
    if not math.isfinite(total) or abs(total - 1.0) > 1e-6:
        raise ScoringError(f"score weights must sum to 1.0, got {total}: {resolved}")
    return {component: float(resolved[component]) for component in _COMPONENTS}


def _validate_unit_interval(name: str, value: float) -> float:
    try:
        resolved = float(value)
    except (TypeError, ValueError) as error:
        raise ScoringError(f"{name} must be numeric, got {value}") from error
    if not math.isfinite(resolved) or not 0.0 <= resolved <= 1.0:
        raise ScoringError(f"{name} must be in [0, 1], got {value}")
    return resolved


def _validity_score_for_feature(
    validity_report: Optional[Dict[str, Any]], feature_index: int
) -> float:
    """Return 0 for an explicitly invalid feature, otherwise 1."""
    if validity_report is None:
        return 1.0
    invalid_indices = {int(index) for index in validity_report.get("invalid_indices", [])}
    return 0.0 if int(feature_index) in invalid_indices else 1.0


def score_feature(
    feature_index: int,
    shape_accuracy: float,
    ai_confidence: Optional[float] = None,
    validity_report: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Compute a composite score for one predicted feature."""
    resolved_weights = _resolve_weights(weights)
    resolved_shape_accuracy = _validate_unit_interval("shape_accuracy", shape_accuracy)

    confidence_was_missing = ai_confidence is None
    resolved_confidence = (
        DEFAULT_AI_CONFIDENCE if confidence_was_missing else _validate_unit_interval(
            "ai_confidence", ai_confidence
        )
    )
    validity_score = _validity_score_for_feature(validity_report, feature_index)
    composite = (
        resolved_weights["geometry_validity"] * validity_score
        + resolved_weights["shape_accuracy"] * resolved_shape_accuracy
        + resolved_weights["ai_confidence"] * resolved_confidence
    )

    return {
        "feature_index": int(feature_index),
        "geometry_validity": validity_score,
        "shape_accuracy": resolved_shape_accuracy,
        "ai_confidence": resolved_confidence,
        "ai_confidence_was_missing": confidence_was_missing,
        "composite_score": round(composite, 6),
    }


def score_layer(
    ai_validation_report: Dict[str, Any],
    ai_confidences: Optional[Dict[int, float]] = None,
    validity_report: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Score all predicted features and aggregate their composite scores."""
    confidences = ai_confidences or {}
    feature_scores: List[Dict[str, Any]] = []

    for true_positive in ai_validation_report.get("true_positives", []):
        index = int(true_positive["predicted_index"])
        feature_scores.append(
            score_feature(
                feature_index=index,
                shape_accuracy=true_positive["iou"],
                ai_confidence=confidences.get(index),
                validity_report=validity_report,
                weights=weights,
            )
        )

    for false_positive in ai_validation_report.get("false_positives", []):
        index = int(false_positive["predicted_index"])
        feature_scores.append(
            score_feature(
                feature_index=index,
                shape_accuracy=false_positive["best_iou"],
                ai_confidence=confidences.get(index),
                validity_report=validity_report,
                weights=weights,
            )
        )

    if not feature_scores:
        return {
            "layer": ai_validation_report.get("layer", "layer"),
            "feature_scores": [],
            "mean_composite_score": 0.0,
            "min_composite_score": 0.0,
            "max_composite_score": 0.0,
        }

    composites = [score["composite_score"] for score in feature_scores]
    return {
        "layer": ai_validation_report.get("layer", "layer"),
        "feature_scores": feature_scores,
        "mean_composite_score": round(sum(composites) / len(composites), 6),
        "min_composite_score": round(min(composites), 6),
        "max_composite_score": round(max(composites), 6),
    }