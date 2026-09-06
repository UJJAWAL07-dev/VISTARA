"""Layer metadata and AI adapter tests."""

import pytest

from gis.config import WGS84
from gis.layers import LayerType, build_raster_layer, build_vector_layer
from gis.layers.ai_adapter import UnsupportedAIOutputError, ai_output_to_layer
from gis.loaders import load_vector


def test_build_vector_layer_metadata(synthetic_parcels_path):
    layer = build_vector_layer(
        load_vector(synthetic_parcels_path),
        layer_id="p1",
        name="Parcels",
        source=synthetic_parcels_path,
    )
    assert layer.type == LayerType.VECTOR
    assert layer.is_vector() and not layer.is_raster()
    assert layer.feature_count == 3
    assert layer.crs == "EPSG:4326"
    assert layer.geometry_type == ["Polygon"]
    assert layer.summary()["id"] == "p1"
    assert "data" not in layer.summary()


def test_build_raster_layer_metadata(synthetic_raster_path):
    layer = build_raster_layer(
        synthetic_raster_path,
        layer_id="r1",
        name="DSM",
    )
    assert layer.type == LayerType.RASTER
    assert layer.is_raster() and not layer.is_vector()
    assert layer.raster_meta["width"] == 10
    assert layer.data is None


def test_ai_adapter_geojson_dict():
    fake = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
            "properties": {"class": "building"},
        }],
    }
    layer = ai_output_to_layer(
        fake,
        layer_id="ai1",
        name="AI Buildings",
        assume_crs=WGS84,
    )
    assert layer.feature_count == 1
    assert layer.metadata["ai_generated"] is True


def test_ai_adapter_unsupported_type_raises():
    with pytest.raises(UnsupportedAIOutputError):
        ai_output_to_layer(12345, layer_id="x", name="x", assume_crs=WGS84)
