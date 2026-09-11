import geopandas as gpd
import pytest

from gis_analysis.exceptions import EmptyLayerError, InconsistentCRSError
from gis_analysis.spatial import (
    assert_consistent_crs,
    find_contained,
    find_overlaps,
    iou,
    spatial_match,
)


def test_iou_partial_overlap(predicted_gdf, ground_truth_gdf):
    assert 0.7 < iou(predicted_gdf.geometry.iloc[0], ground_truth_gdf.geometry.iloc[0]) < 0.9


def test_iou_no_overlap_returns_zero(predicted_gdf, ground_truth_gdf):
    assert iou(predicted_gdf.geometry.iloc[1], ground_truth_gdf.geometry.iloc[0]) == 0.0


def test_find_overlaps_detects_pair(overlapping_gdf):
    assert find_overlaps(overlapping_gdf, layer_name="test") == [(0, 1)]


def test_find_overlaps_empty_layer_raises():
    empty = gpd.GeoDataFrame({"id": []}, geometry=[], crs="EPSG:32643")
    with pytest.raises(EmptyLayerError):
        find_overlaps(empty, layer_name="test")


def test_find_contained_matches_and_excludes(parcels_gdf, buildings_gdf):
    assert find_contained(parcels_gdf, buildings_gdf, layer_name="test") == [(0, 0), (1, None)]


def test_spatial_match_classifies_correctly(predicted_gdf, ground_truth_gdf):
    matches = spatial_match(predicted_gdf, ground_truth_gdf, 0.5, "test")
    assert matches[0]["is_match"] is True
    assert matches[1]["is_match"] is False
    assert matches[1]["matched_gt_index"] is None


def test_assert_consistent_crs_passes_when_matching(predicted_gdf, ground_truth_gdf):
    assert assert_consistent_crs(predicted_gdf, ground_truth_gdf, context="test") == "EPSG:32643"


def test_assert_consistent_crs_raises_on_mismatch(predicted_gdf):
    with pytest.raises(InconsistentCRSError):
        assert_consistent_crs(predicted_gdf, predicted_gdf.to_crs("EPSG:4326"), context="test")