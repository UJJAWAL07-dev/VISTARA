"""
VISTARA — Combined GIS Engine + GIS Analysis Engine Demo

Chains the two packages Member 4/5 own into one live walkthrough.
"""

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import geopandas as gpd

from gis.config import WGS84, get_utm_epsg
from gis.services import ingest_ai_layer
from gis_analysis.services import generate_full_report


def section(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    section("1. Simulated inputs: AI-predicted parcels + ground truth")

    ground_truth_wgs84 = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[
                    [77.2000, 28.6000], [77.2010, 28.6000],
                    [77.2010, 28.6010], [77.2000, 28.6010], [77.2000, 28.6000],
                ]]},
                "properties": {"gt_id": "GT-1", "land_use": "residential"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[
                    [77.2100, 28.6100], [77.2110, 28.6100],
                    [77.2110, 28.6110], [77.2100, 28.6110], [77.2100, 28.6100],
                ]]},
                "properties": {"gt_id": "GT-2", "land_use": "commercial"},
            },
        ],
    }

    ai_predicted_wgs84 = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[
                    [77.20005, 28.60005], [77.20105, 28.60005],
                    [77.20105, 28.60105], [77.20005, 28.60105], [77.20005, 28.60005],
                ]]},
                "properties": {"pred_id": "AI-1", "land_use": "residential", "confidence": 0.93},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[
                    [77.2003, 28.6003], [77.2013, 28.6003],
                    [77.2013, 28.6013], [77.2003, 28.6013], [77.2003, 28.6003],
                ]]},
                "properties": {"pred_id": "AI-2", "land_use": "residential", "confidence": 0.61},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[
                    [77.3000, 28.7000], [77.3010, 28.7000],
                    [77.3010, 28.7010], [77.3000, 28.7010], [77.3000, 28.7000],
                ]]},
                "properties": {"pred_id": "AI-3", "land_use": "industrial", "confidence": 0.40},
            },
        ],
    }

    print("Ground truth features:", len(ground_truth_wgs84["features"]))
    print("AI predicted features:", len(ai_predicted_wgs84["features"]))

    section("2. gis.services — ingest AI output into a GIS-ready Layer")
    utm_epsg = get_utm_epsg(77.2, 28.6)
    ai_layer = ingest_ai_layer(
        ai_predicted_wgs84,
        layer_id="ai_predicted_parcels",
        name="AI Predicted Parcels",
        assume_crs=WGS84,
        target_crs=utm_epsg,
    )
    print(json.dumps(ai_layer.summary(), indent=2, default=str))

    section("3. gis.services — prepare ground truth via the same pipeline")
    gt_gdf = gpd.GeoDataFrame.from_features(ground_truth_wgs84["features"], crs=WGS84)
    gt_gdf = gt_gdf.to_crs(utm_epsg)
    print(f"Ground truth reprojected to {utm_epsg}, {len(gt_gdf)} features")

    section("4. gis_analysis.services — run the full analysis")
    report = generate_full_report(
        layer_name="ai_predicted_parcels",
        predicted_gdf=ai_layer.data,
        ground_truth_gdf=gt_gdf,
        validity_report=ai_layer.metadata["validity_before_processing"],
        ai_confidences={
            i: float(ai_layer.data["confidence"].iloc[i])
            for i in range(len(ai_layer.data))
            if "confidence" in ai_layer.data.columns
        },
        run_landuse=True,
    )
    print(json.dumps(report, indent=2, default=str))

    section("5. Judge-facing summary")
    print(f"Layer: {report['layer']}")
    print(f"Overall status: {report['overall']['status']}")
    if report["overall"]["reasons"]:
        print("Reasons:")
        for reason in report["overall"]["reasons"]:
            print(f"  - {reason}")
    print(f"Mean AI confidence score: {report['scoring']['mean_composite_score']:.3f}")
    print(f"Precision: {report['statistics']['precision']:.2f} | "
          f"Recall: {report['statistics']['recall']:.2f} | "
          f"F1: {report['statistics']['f1']:.2f}")

    section("Demo complete")
    print("gis.services -> gis_analysis.services pipeline validated end-to-end.")


if __name__ == "__main__":
    main()
