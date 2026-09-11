"""
Geometry validation, repair, and simplification (section 19).

Repair is opt-in and never automatic or silent. Original data is
preserved wherever possible; repair operates on a copy.
"""

from typing import Any, Dict

import geopandas as gpd

from gis.exceptions import GeometryValidationError


def check_validity(
    gdf: gpd.GeoDataFrame,
    layer_name: str = "layer",
) -> Dict[str, Any]:
    """Inspect geometry validity without modifying the GeoDataFrame."""
    if len(gdf) == 0:
        return {
            "total": 0,
            "invalid_count": 0,
            "invalid_indices": [],
            "is_all_valid": True,
        }

    valid_mask = gdf.geometry.is_valid
    invalid_indices = gdf.index[~valid_mask].tolist()

    return {
        "total": len(gdf),
        "invalid_count": len(invalid_indices),
        "invalid_indices": invalid_indices,
        "is_all_valid": len(invalid_indices) == 0,
    }


def repair_geometry(
    gdf: gpd.GeoDataFrame,
    layer_name: str = "layer",
    strict: bool = False,
) -> gpd.GeoDataFrame:
    """
    Attempt to repair invalid geometries with the buffer(0) heuristic.

    Returns a new GeoDataFrame and never mutates the input. With
    ``strict=True``, raises if any geometry remains invalid afterward.
    """
    report = check_validity(gdf, layer_name)
    if report["is_all_valid"]:
        return gdf.copy()

    repaired = gdf.copy()
    invalid_idx = report["invalid_indices"]
    repaired.loc[invalid_idx, "geometry"] = repaired.loc[
        invalid_idx, "geometry"
    ].buffer(0)

    if strict:
        post_report = check_validity(repaired, layer_name)
        if not post_report["is_all_valid"]:
            raise GeometryValidationError(
                layer_name,
                f"{post_report['invalid_count']} of {post_report['total']} "
                "geometries remain invalid after repair attempt.",
            )

    return repaired


def simplify_geometry(
    gdf: gpd.GeoDataFrame,
    tolerance: float,
    preserve_topology: bool = True,
) -> gpd.GeoDataFrame:
    """Simplify geometries in the units of the GeoDataFrame's CRS."""
    simplified = gdf.copy()
    simplified["geometry"] = simplified.geometry.simplify(
        tolerance,
        preserve_topology=preserve_topology,
    )
    return simplified
