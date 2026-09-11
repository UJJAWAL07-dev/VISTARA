import geopandas as gpd
import pytest

from gis_analysis.exceptions import InvalidInputError
from gis_analysis.statistics import calculate_accuracy_metrics, summarize_layer


def test_accuracy_metrics_from_report(ai_validation_report):
    stats = calculate_accuracy_metrics(ai_validation_report)
    assert stats["precision"] == 0.5
    assert stats["recall"] == 0.5
    assert stats["f1"] == 0.5
    assert 0.7 < stats["mean_iou"] < 0.9


def test_accuracy_metrics_zero_true_positives_safe():
    report = {
        "iou_threshold": 0.5,
        "true_positive_count": 0,
        "false_positive_count": 2,
        "false_negative_count": 2,
        "true_positives": [],
    }
    stats = calculate_accuracy_metrics(report)
    assert stats["precision"] == stats["recall"] == stats["f1"] == stats["mean_iou"] == 0.0


def test_accuracy_metrics_invalid_input_raises():
    with pytest.raises(InvalidInputError):
        calculate_accuracy_metrics({}, predicted_gdf=object())


def test_summary_stats_area_totals(ground_truth_gdf):
    stats = summarize_layer(ground_truth_gdf, layer_name="test")
    assert stats["feature_count"] == 2
    assert stats["total_area"] == 200.0
    assert stats["mean_area"] == 100.0


def test_summary_stats_empty_layer_safe():
    empty = gpd.GeoDataFrame({"id": []}, geometry=[], crs="EPSG:32643")
    stats = summarize_layer(empty, layer_name="test")
    assert stats["feature_count"] == 0
    assert stats["total_area"] == 0.0