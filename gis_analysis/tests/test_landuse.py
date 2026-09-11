import geopandas as gpd
from shapely.geometry import Polygon

from gis_analysis.landuse import calculate_area_breakdown, check_classification_consistency, check_internal_classification_consistency

CRS = "EPSG:32643"


def test_classification_consistency_agreement_rate():
    predicted = gpd.GeoDataFrame({"land_use": ["residential", "commercial"]}, geometry=[
        Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]), Polygon([(20, 0), (30, 0), (30, 10), (20, 10)])
    ], crs=CRS)
    ground_truth = gpd.GeoDataFrame({"land_use": ["residential", "industrial"]}, geometry=[
        Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]), Polygon([(20, 0), (30, 0), (30, 10), (20, 10)])
    ], crs=CRS)
    report = {"true_positives": [
        {"predicted_index": 0, "matched_gt_index": 0},
        {"predicted_index": 1, "matched_gt_index": 1},
    ]}
    result = check_classification_consistency(predicted, ground_truth, report)
    assert result["agreement_rate"] == 0.5
    assert result["disagree_count"] == 1


def test_internal_consistency_flags_conflicting_overlap():
    gdf = gpd.GeoDataFrame({"land_use": ["residential", "commercial"]}, geometry=[
        Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]), Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
    ], crs=CRS)
    assert check_internal_classification_consistency(gdf)["conflict_count"] == 1


def test_area_breakdown_percentages(ground_truth_gdf):
    result = calculate_area_breakdown(ground_truth_gdf)
    assert result["total_area"] == 200.0
    assert result["categories"]["residential"]["percentage"] == 50.0
    assert result["categories"]["commercial"]["percentage"] == 50.0