"""Geometry validation, repair, and clipping tests."""

import pytest

from gis.config import WGS84
from gis.exceptions import AOIError
from gis.loaders import load_vector
from gis.processing import check_validity, clip_to_aoi, repair_geometry


def test_check_validity_on_clean_data(synthetic_parcels_path):
    report = check_validity(load_vector(synthetic_parcels_path), layer_name="test")
    assert report["is_all_valid"] is True
    assert report["invalid_count"] == 0


def test_repair_geometry_is_noop_on_valid_data(synthetic_parcels_path):
    gdf = load_vector(synthetic_parcels_path)
    repaired = repair_geometry(gdf, layer_name="test")
    assert len(repaired) == len(gdf)
    assert check_validity(repaired, layer_name="test")["is_all_valid"] is True


def test_clip_to_aoi_reduces_features(synthetic_parcels_path):
    clipped = clip_to_aoi(
        load_vector(synthetic_parcels_path),
        (77.199, 28.599, 77.2035, 28.601),
        aoi_crs=WGS84,
        layer_name="test",
    )
    assert len(clipped) == 2


def test_clip_with_mismatched_crs_raises(synthetic_parcels_path):
    with pytest.raises(AOIError):
        clip_to_aoi(
            load_vector(synthetic_parcels_path),
            (0, 0, 1, 1),
            aoi_crs="EPSG:32643",
            layer_name="test",
        )


def test_clip_with_no_overlap_raises(synthetic_parcels_path):
    with pytest.raises(AOIError):
        clip_to_aoi(
            load_vector(synthetic_parcels_path),
            (0, 0, 1, 1),
            aoi_crs=WGS84,
            layer_name="test",
        )
