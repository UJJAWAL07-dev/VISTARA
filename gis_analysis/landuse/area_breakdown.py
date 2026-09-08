"""Area totals and percentages by land-use category."""

from typing import Any, Dict, Optional

import geopandas as gpd
from shapely.geometry.base import BaseGeometry

from gis_analysis.exceptions import InvalidInputError
from gis_analysis.spatial.geometry_metrics import area_of


def calculate_area_breakdown(
    gdf: gpd.GeoDataFrame,
    category_column: str = "land_use",
    aoi: Optional[BaseGeometry] = None,
) -> Dict[str, Any]:
    """Return total and percentage area for each category.

    Areas use the GeoDataFrame's current CRS units. When ``aoi`` is supplied,
    each feature is intersected with it before area is calculated.
    """
    if category_column not in gdf.columns:
        raise InvalidInputError(f"missing category column '{category_column}'")

    totals: Dict[str, float] = {}
    for row in gdf.itertuples(index=False):
        geometry = getattr(row, gdf.geometry.name)
        if aoi is not None:
            geometry = geometry.intersection(aoi) if geometry is not None else None
        category = getattr(row, category_column)
        category_name = "unknown" if category is None else str(category)
        totals[category_name] = totals.get(category_name, 0.0) + area_of(geometry)

    total_area = sum(totals.values())
    categories = {
        category: {
            "area": round(area, 6),
            "percentage": round(area / total_area * 100, 6) if total_area else 0.0,
        }
        for category, area in sorted(totals.items())
    }
    return {
        "category_column": category_column,
        "feature_count": len(gdf),
        "total_area": round(total_area, 6),
        "categories": categories,
    }