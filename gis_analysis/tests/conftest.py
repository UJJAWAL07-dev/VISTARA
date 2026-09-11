"""Shared synthetic GeoDataFrame fixtures for GIS analysis tests."""

import geopandas as gpd
import pytest
from shapely.geometry import Polygon

CRS = "EPSG:32643"


@pytest.fixture
def ground_truth_gdf():
    return gpd.GeoDataFrame(
        {"gt_id": ["GT-1", "GT-2"], "land_use": ["residential", "commercial"]},
        geometry=[
            Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
            Polygon([(200, 200), (210, 200), (210, 210), (200, 210)]),
        ],
        crs=CRS,
    )


@pytest.fixture
def predicted_gdf():
    return gpd.GeoDataFrame(
        {"pred_id": ["AI-1", "AI-2"], "land_use": ["residential", "residential"]},
        geometry=[
            Polygon([(0.5, 0.5), (9.5, 0.5), (9.5, 9.5), (0.5, 9.5)]),
            Polygon([(500, 500), (510, 500), (510, 510), (500, 510)]),
        ],
        crs=CRS,
    )


@pytest.fixture
def overlapping_gdf():
    return gpd.GeoDataFrame(
        {"id": [1, 2, 3]},
        geometry=[
            Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
            Polygon([(5, 5), (15, 5), (15, 15), (5, 15)]),
            Polygon([(50, 50), (60, 50), (60, 60), (50, 60)]),
        ],
        crs=CRS,
    )


@pytest.fixture
def parcels_gdf():
    return gpd.GeoDataFrame(
        {"parcel_id": ["P1"]},
        geometry=[Polygon([(0, 0), (20, 0), (20, 20), (0, 20)])],
        crs=CRS,
    )


@pytest.fixture
def buildings_gdf():
    return gpd.GeoDataFrame(
        {"building_id": ["B1", "B2"]},
        geometry=[
            Polygon([(2, 2), (4, 2), (4, 4), (2, 4)]),
            Polygon([(100, 100), (102, 100), (102, 102), (100, 102)]),
        ],
        crs=CRS,
    )


@pytest.fixture
def ai_validation_report(predicted_gdf, ground_truth_gdf):
    from gis_analysis.validation import validate_against_ground_truth

    return validate_against_ground_truth(
        predicted_gdf, ground_truth_gdf, iou_threshold=0.5, layer_name="parcels"
    )