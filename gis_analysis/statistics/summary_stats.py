"""Basic feature-count and geometry-area summaries."""

from statistics import mean, median
from typing import Any, Dict

import geopandas as gpd

from gis_analysis.spatial.geometry_metrics import area_of


def summarize_layer(
    gdf: gpd.GeoDataFrame,
    layer_name: str = "layer",
) -> Dict[str, Any]:
    """Return feature count and area distribution for a GeoDataFrame.

    Area values use the GeoDataFrame's current CRS units. Callers should
    provide a projected CRS when area is intended to represent metric units.
    Empty or missing geometries contribute an area of zero.
    """
    areas = [float(area_of(geometry)) for geometry in gdf.geometry]
    return {
        "layer": layer_name,
        "feature_count": len(gdf),
        "total_area": sum(areas),
        "min_area": min(areas) if areas else 0.0,
        "max_area": max(areas) if areas else 0.0,
        "mean_area": mean(areas) if areas else 0.0,
        "median_area": median(areas) if areas else 0.0,
        "area_distribution": areas,
    }