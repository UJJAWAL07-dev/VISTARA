"""Vector/raster loading and metadata inspection tests."""

import pytest

from gis.exceptions import FileNotFoundInGISError, UnsupportedFormatError
from gis.loaders import inspect_raster, inspect_vector, load_raster, load_vector


def test_load_vector_success(synthetic_parcels_path):
    gdf = load_vector(synthetic_parcels_path)
    assert len(gdf) == 3
    assert gdf.crs is not None


def test_inspect_vector_metadata(synthetic_parcels_path):
    info = inspect_vector(load_vector(synthetic_parcels_path))
    assert info["feature_count"] == 3
    assert info["crs"] == "EPSG:4326"
    assert info["geometry_types"] == ["Polygon"]
    assert "parcel_id" in info["columns"]


def test_load_vector_missing_file():
    with pytest.raises(FileNotFoundInGISError):
        load_vector("does_not_exist.geojson")


def test_load_vector_unsupported_format(tmp_path):
    bad_file = tmp_path / "data.txt"
    bad_file.write_text("not geo data")
    with pytest.raises(UnsupportedFormatError):
        load_vector(bad_file)


def test_load_raster_success(synthetic_raster_path):
    with load_raster(synthetic_raster_path) as dataset:
        assert dataset.width == 10
        assert dataset.height == 10


def test_inspect_raster_metadata(synthetic_raster_path):
    info = inspect_raster(synthetic_raster_path)
    assert info["width"] == 10
    assert info["height"] == 10
    assert info["crs"] == "EPSG:4326"
    assert info["band_count"] == 1
    assert info["dtype"] == "uint8"
