"""End-to-end GIS analysis demo workflow for synthetic VISTARA inputs."""

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import geopandas as gpd
from shapely.geometry import Polygon

from gis_analysis.services import generate_full_report


CRS = "EPSG:32643"


def section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def build_synthetic_demo_inputs() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Create a tiny AI-vs-ground-truth scenario that exercises reporting.

    The predicted layer intentionally contains one clean match, one deliberate
    overlap violation, and one false-positive parcel outside the ground truth.
    """
    ground_truth_gdf = gpd.GeoDataFrame(
        {
            "gt_id": ["GT-1", "GT-2"],
            "land_use": ["residential", "commercial"],
        },
        geometry=[
            Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
            Polygon([(20, 20), (30, 20), (30, 30), (20, 30)]),
        ],
        crs=CRS,
    )

    predicted_gdf = gpd.GeoDataFrame(
        {
            "pred_id": ["AI-1", "AI-2", "AI-3"],
            "land_use": ["residential", "commercial", "residential"],
        },
        geometry=[
            Polygon([(0.5, 0.5), (9.5, 0.5), (9.5, 9.5), (0.5, 9.5)]),
            Polygon([(5, 5), (15, 5), (15, 15), (5, 15)]),
            Polygon([(100, 100), (110, 100), (110, 110), (100, 110)]),
        ],
        crs=CRS,
    )

    return ground_truth_gdf, predicted_gdf


def main() -> None:
    section("1. Synthetic AI-vs-ground-truth scenario")
    ground_truth_gdf, predicted_gdf = build_synthetic_demo_inputs()
    print(json.dumps({
        "ground_truth_features": len(ground_truth_gdf),
        "predicted_features": len(predicted_gdf),
        "crs": ground_truth_gdf.crs,
    }, indent=2, default=str))

    section("2. Run the public analysis facade")
    report = generate_full_report(
        layer_name="synthetic_parcels",
        predicted_gdf=predicted_gdf,
        ground_truth_gdf=ground_truth_gdf,
        run_landuse=True,
        pass_score_threshold=0.6,
    )

    print(json.dumps(report, indent=2, default=str))

    section("Demo complete")
    print("GIS analysis Phase 9 demo exercised validation, stats, scoring, land-use, and report assembly on a synthetic AI-vs-ground-truth scenario.")


if __name__ == "__main__":
    main()
