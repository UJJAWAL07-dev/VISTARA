import pytest

from gis_analysis.exceptions import ScoringError
from gis_analysis.scoring import score_feature, score_layer


def test_score_feature_default_confidence():
    result = score_feature(0, shape_accuracy=0.81)
    assert result["ai_confidence"] == 0.5
    assert result["ai_confidence_was_missing"] is True
    assert abs(result["composite_score"] - 0.774) < 1e-6


def test_score_feature_with_confidence():
    result = score_feature(0, shape_accuracy=0.81, ai_confidence=0.95)
    assert result["ai_confidence_was_missing"] is False
    assert abs(result["composite_score"] - 0.909) < 1e-6


def test_score_feature_bad_weights_raises():
    with pytest.raises(ScoringError):
        score_feature(0, 0.5, weights={"geometry_validity": 0.5, "shape_accuracy": 0.5, "ai_confidence": 0.5})


def test_score_feature_out_of_range_raises():
    with pytest.raises(ScoringError):
        score_feature(0, 1.5)


def test_score_layer_aggregates_correctly(ai_validation_report):
    result = score_layer(ai_validation_report)
    assert len(result["feature_scores"]) == 2
    assert abs(result["mean_composite_score"] - 0.612) < 1e-6