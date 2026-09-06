"""CRS transformation and GeoJSON conversion tests."""

import json

import geopandas as gpd
import pytest

from gis.config import WGS84, get_utm_epsg
from gis.conversion import (
    convert_to_geojson,
    reproject_vector,
    vector_to_geojson_dict,
)
from gis.exceptions import MissingCRSError
from gis.loaders import load_vector


def test_reproject_to_utm_and_back(synthetic_parcels_path):
    gdf = load_vector(synthetic_parcels_path)
    utm_epsg = get_utm_epsg(77.2, 28.6)
    gdf_utm = reproject_vector(gdf, utm_epsg, layer_name="test")
    assert str(gdf_utm.crs) == utm_epsg
    assert all(area > 0 for area in gdf_utm.geometry.area)

    gdf_back = reproject_vector(gdf_utm, WGS84, layer_name="test")
    assert str(gdf_back.crs) == WGS84


def test_reproject_missing_crs_raises(synthetic_parcels_path):
    gdf = load_vector(synthetic_parcels_path)
    gdf_no_crs = gdf.copy()
    gdf_no_crs.crs = None
    with pytest.raises(MissingCRSError):
        reproject_vector(gdf_no_crs, WGS84, layer_name="test")


def test_convert_to_geojson_file(synthetic_parcels_path, tmp_path):
    result_path = convert_to_geojson(
        load_vector(synthetic_parcels_path),
        tmp_path / "out.geojson",
        layer_name="test",
    )
    assert result_path.exists()
    with result_path.open() as file:
        data = json.load(file)
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 3


def test_vector_to_geojson_dict_preserves_properties(synthetic_parcels_path):
    data = vector_to_geojson_dict(load_vector(synthetic_parcels_path), layer_name="test")
    assert data["type"] == "FeatureCollection"
    assert "parcel_id" in data["features"][0]["properties"]
    assert "land_use" in data["features"][0]["properties"]
