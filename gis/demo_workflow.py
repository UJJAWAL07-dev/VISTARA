"""End-to-end VISTARA GIS demo using clearly labeled synthetic data."""

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gis.config import WGS84, get_utm_epsg
from gis.loaders.synthetic_fixtures import (
    make_synthetic_parcels,
    make_synthetic_raster,
)
from gis.services import (
    get_analysis_ready_bundle_summary,
    get_layer_geojson,
    ingest_ai_layer,
    load_and_prepare_vector_layer,
    load_raster_layer,
    prepare_layer_bundle,
)


def section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    section("1. Synthetic sample data")
    parcels_path = make_synthetic_parcels()
    raster_path = make_synthetic_raster()
    print(f"Parcels: {parcels_path}")
    print(f"Raster:  {raster_path}")

    section("2. Load and prepare a vector layer")
    parcel_layer = load_and_prepare_vector_layer(
        parcels_path,
        layer_id="parcel_layer",
        name="Parcels",
        target_crs=WGS84,
    )
    print(json.dumps(parcel_layer.summary(), indent=2, default=str))

    section("3. Convert to browser-facing GeoJSON")
    geojson = get_layer_geojson(parcel_layer)
    print(f"FeatureCollection with {len(geojson['features'])} features")

    section("4. Load a raster layer")
    raster_layer = load_raster_layer(
        raster_path,
        layer_id="dsm_layer",
        name="Synthetic DSM",
    )
    print(json.dumps(raster_layer.summary(), indent=2, default=str))

    section("5. Ingest a simulated AI output")
    fake_ai_output = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [77.2001, 28.6001],
                    [77.2004, 28.6001],
                    [77.2004, 28.6004],
                    [77.2001, 28.6004],
                    [77.2001, 28.6001],
                ]],
            },
            "properties": {"class": "building", "confidence": 0.93},
        }],
    }
    ai_layer = ingest_ai_layer(
        fake_ai_output,
        layer_id="ai_building_layer",
        name="AI Building Footprints",
        assume_crs=WGS84,
    )
    print(json.dumps(ai_layer.summary(), indent=2, default=str))

    section("6. Bundle layers for the GIS Analysis Engine")
    bundle = prepare_layer_bundle(
        layer_specs=[
            {"path": parcels_path, "layer_id": "parcel_layer", "name": "Parcels"},
        ],
        target_crs=get_utm_epsg(77.2, 28.6),
    )
    print(json.dumps(get_analysis_ready_bundle_summary(bundle), indent=2, default=str))

    section("Demo complete")
    print("All GIS engine phases exercised successfully on synthetic data.")


if __name__ == "__main__":
    main()
