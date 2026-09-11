"""Backend service facade and sample workflow tests."""

import pytest

from gis.config import WGS84, get_utm_epsg
from gis.exceptions import GISEngineError
from gis.services import (
    get_analysis_ready_bundle_summary,
    get_layer_geojson,
    list_sample_layers,
    load_and_prepare_vector_layer,
    load_raster_layer,
    prepare_layer_bundle,
)


def test_list_sample_layers_returns_expected_categories():
    result = list_sample_layers()
    assert set(result) == {"vector", "raster"}
    assert set(result["vector"]) == {"parcels", "buildings", "roads", "land-use"}
    assert set(result["raster"]) == {"imagery", "dsm", "dtm"}


def test_load_and_prepare_vector_layer_via_service(synthetic_parcels_path):
    layer = load_and_prepare_vector_layer(
        synthetic_parcels_path,
        layer_id="p1",
        name="Parcels",
        target_crs=WGS84,
    )
    assert layer.feature_count == 3
    assert get_layer_geojson(layer)["type"] == "FeatureCollection"


def test_load_raster_layer_via_service(synthetic_raster_path):
    layer = load_raster_layer(synthetic_raster_path, layer_id="r1", name="DSM")
    assert layer.raster_meta["width"] == 10


def test_service_raises_typed_error_for_missing_file():
    with pytest.raises(GISEngineError):
        load_and_prepare_vector_layer("missing.geojson", layer_id="x", name="x")


def test_prepare_layer_bundle_shares_crs(synthetic_parcels_path):
    bundle = prepare_layer_bundle(
        layer_specs=[
            {"path": synthetic_parcels_path, "layer_id": "a", "name": "A"},
            {"path": synthetic_parcels_path, "layer_id": "b", "name": "B"},
        ],
        target_crs=get_utm_epsg(77.2, 28.6),
    )
    summary = get_analysis_ready_bundle_summary(bundle)
    assert summary["consistent_crs"] is True
    assert summary["layer_count"] == 2
