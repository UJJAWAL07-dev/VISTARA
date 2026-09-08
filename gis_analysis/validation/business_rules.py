"""Business-rule validation for parcel and building layers."""

from typing import Any, Dict

import geopandas as gpd

from gis_analysis.spatial.relationships import find_contained, find_overlaps


def validate_no_overlaps(
    gdf: gpd.GeoDataFrame,
    layer_name: str = "parcels",
) -> Dict[str, Any]:
    """Validate that features do not share positive-area geometry."""
    overlap_pairs = find_overlaps(gdf, layer_name=layer_name)
    violations = [
        {"feature_index_a": first, "feature_index_b": second}
        for first, second in overlap_pairs
    ]
    return {
        "rule": "no_overlaps",
        "layer": layer_name,
        "valid": not violations,
        "checked_count": len(gdf),
        "violation_count": len(violations),
        "violations": violations,
    }


def validate_must_be_contained_in(
    container_gdf: gpd.GeoDataFrame,
    contained_gdf: gpd.GeoDataFrame,
    container_name: str = "parcels",
    contained_name: str = "buildings",
) -> Dict[str, Any]:
    """Validate that every contained-layer feature belongs to a container."""
    containment = find_contained(
        container_gdf,
        contained_gdf,
        layer_name=f"{contained_name}_in_{container_name}",
    )
    matches = [
        {"contained_index": contained_index, "container_index": container_index}
        for contained_index, container_index in containment
        if container_index is not None
    ]
    violations = [
        {"contained_index": contained_index, "container_index": None}
        for contained_index, container_index in containment
        if container_index is None
    ]
    return {
        "rule": "must_be_contained_in",
        "container_layer": container_name,
        "contained_layer": contained_name,
        "valid": not violations,
        "checked_count": len(containment),
        "match_count": len(matches),
        "violation_count": len(violations),
        "matches": matches,
        "violations": violations,
    }