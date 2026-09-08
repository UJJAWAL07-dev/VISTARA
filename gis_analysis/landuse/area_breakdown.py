"""Area totals and percentages by land-use category."""

from typing import Any, Dict, Optional

import geopandas as gpd
from shapely.geometry.base import BaseGeometry

from gis_analysis.exceptions import InvalidInputError
from gis_analysis.spatial.geometry_metrics import area_of


def _json_value(value: Any) -> Any:
    return value.item() if hasattr(value, "item") else value


def calculate_area_breakdown(
    gdf: gpd.GeoDataFrame,
    label_column: str = "land_use",
    aoi_geometry: Optional[BaseGeometry] = None,
) -> Dict[str, Any]:
    """Compute total and percentage area per label without mutating the layer."""
    if label_column not in gdf.columns:
        raise InvalidInputError(f"'{label_column}' column not found in gdf")

    if len(gdf) == 0:
        return {
            "label_column": label_column,
            "total_area": 0.0,
            "feature_count": 0,
            "categories": {},
        }

    category_totals: Dict[Any, Dict[str, Any]] = {}
    for geometry, label in zip(gdf.geometry, gdf[label_column]):
        if aoi_geometry is not None:
            geometry = (
                geometry.intersection(aoi_geometry)
                if geometry is not None and not geometry.is_empty
                else None
            )
        category = _json_value(label)
        if category is None:
            category = "unknown"
        summary = category_totals.setdefault(
            category, {"area": 0.0, "feature_count": 0}
        )
        summary["area"] += area_of(geometry)
        summary["feature_count"] += 1

    total_area = sum(summary["area"] for summary in category_totals.values())
    categories = {
        category: {
            "area": float(summary["area"]),
            "percentage": round(summary["area"] / total_area * 100, 4)
            if total_area > 0
            else 0.0,
            "feature_count": summary["feature_count"],
        }
        for category, summary in category_totals.items()
    }
    return {
        "label_column": label_column,
        "total_area": float(total_area),
        "feature_count": len(gdf),
        "categories": categories,
    }