"""Business-rule validation for spatial layers."""

from typing import Any, Dict

import geopandas as gpd

from gis_analysis.exceptions import ValidationRuleError
from gis_analysis.spatial.relationships import find_contained, find_overlaps


def check_no_overlap(gdf: gpd.GeoDataFrame, layer_name: str = "layer") -> Dict[str, Any]:
    """Check that no two features in a layer share positive-area geometry."""
    try:
        overlaps = find_overlaps(gdf, layer_name=layer_name)
    except Exception as error:
        raise ValidationRuleError("no_overlap", str(error)) from error

    return {
        "rule": "no_overlap",
        "layer": layer_name,
        "total_features": len(gdf),
        "violation_count": len(overlaps),
        "violations": overlaps,
        "passed": len(overlaps) == 0,
    }


def check_contained_within(
    inner_gdf: gpd.GeoDataFrame,
    outer_gdf: gpd.GeoDataFrame,
    inner_name: str = "inner_layer",
    outer_name: str = "outer_layer",
) -> Dict[str, Any]:
    """Check that every inner-layer feature is contained by an outer feature."""
    try:
        results = find_contained(
            outer_gdf,
            inner_gdf,
            layer_name=f"{inner_name}_in_{outer_name}",
        )
    except Exception as error:
        raise ValidationRuleError("contained_within", str(error)) from error

    matches = [
        (inner_index, outer_index)
        for inner_index, outer_index in results
        if outer_index is not None
    ]
    violations = [
        inner_index for inner_index, outer_index in results if outer_index is None
    ]
    return {
        "rule": "contained_within",
        "inner_layer": inner_name,
        "outer_layer": outer_name,
        "total_inner_features": len(inner_gdf),
        "violation_count": len(violations),
        "violations": violations,
        "matches": matches,
        "passed": len(violations) == 0,
    }