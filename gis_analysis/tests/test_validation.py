import pytest

from gis_analysis.validation import check_contained_within, check_no_overlap, validate_against_ground_truth


def test_check_no_overlap_detects_violation(overlapping_gdf):
    report = check_no_overlap(overlapping_gdf, layer_name="test")
    assert report["passed"] is False
    assert report["violation_count"] == 1
    assert report["violations"] == [(0, 1)]


def test_check_no_overlap_passes_when_clean(parcels_gdf):
    report = check_no_overlap(parcels_gdf, layer_name="test")
    assert report["passed"] is True


def test_check_contained_within(parcels_gdf, buildings_gdf):
    report = check_contained_within(buildings_gdf, parcels_gdf, "buildings", "parcels")
    assert report["passed"] is False
    assert report["violation_count"] == 1
    assert (0, 0) in report["matches"]


def test_validate_against_ground_truth_classification(predicted_gdf, ground_truth_gdf):
    report = validate_against_ground_truth(predicted_gdf, ground_truth_gdf, layer_name="test")
    assert report["true_positive_count"] == 1
    assert report["false_positive_count"] == 1
    assert report["false_negative_count"] == 1
    assert report["true_positives"][0]["predicted_index"] == 0