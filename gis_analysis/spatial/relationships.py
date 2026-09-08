"""Layer-level spatial relationship operations for analysis workflows."""

from typing import List, Optional, Tuple

import geopandas as gpd

from gis_analysis.exceptions import EmptyLayerError
from gis_analysis.spatial.crs_check import assert_consistent_crs
from gis_analysis.spatial.geometry_metrics import iou


def find_overlaps(gdf: gpd.GeoDataFrame, layer_name: str = "layer") -> List[Tuple[int, int]]:
    """Find unique pairs of features with positive-area intersections.

    Boundary-touching parcels are allowed; containment and crossing overlaps
    are reported because both create shared polygon area.
    """
    if len(gdf) == 0:
        raise EmptyLayerError(layer_name)

    sindex = gdf.sindex
    overlaps = []
    for i, geom in enumerate(gdf.geometry):
        if geom is None or geom.is_empty:
            continue
        for j in sindex.intersection(geom.bounds):
            if j <= i:
                continue
            other = gdf.geometry.iloc[j]
            if other is None or other.is_empty:
                continue
            if geom.intersection(other).area > 0:
                overlaps.append((i, int(j)))

    return overlaps


def find_contained(
    container_gdf: gpd.GeoDataFrame,
    contained_gdf: gpd.GeoDataFrame,
    layer_name: str = "layers",
) -> List[Tuple[int, Optional[int]]]:
    """Map each contained feature to a containing feature, if one exists."""
    if len(container_gdf) == 0:
        raise EmptyLayerError(f"{layer_name} (container)")
    if len(contained_gdf) == 0:
        raise EmptyLayerError(f"{layer_name} (contained)")

    assert_consistent_crs(container_gdf, contained_gdf, context="find_contained")

    sindex = container_gdf.sindex
    results = []
    for i, geom in enumerate(contained_gdf.geometry):
        if geom is None or geom.is_empty:
            results.append((i, None))
            continue
        match = None
        for j in sindex.intersection(geom.bounds):
            container_geom = container_gdf.geometry.iloc[j]
            if container_geom is not None and container_geom.covers(geom):
                match = int(j)
                break
        results.append((i, match))

    return results


def spatial_match(
    predicted_gdf: gpd.GeoDataFrame,
    ground_truth_gdf: gpd.GeoDataFrame,
    iou_threshold: float,
    layer_name: str = "layers",
) -> List[dict]:
    """Match each predicted feature to its best-overlapping ground-truth feature."""
    if len(predicted_gdf) == 0:
        raise EmptyLayerError(f"{layer_name} (predicted)")
    if len(ground_truth_gdf) == 0:
        raise EmptyLayerError(f"{layer_name} (ground_truth)")
    if not 0 <= iou_threshold <= 1:
        raise ValueError("iou_threshold must be between 0 and 1")

    assert_consistent_crs(predicted_gdf, ground_truth_gdf, context="spatial_match")

    gt_sindex = ground_truth_gdf.sindex
    results = []
    for i, pred_geom in enumerate(predicted_gdf.geometry):
        best_iou = 0.0
        best_j = None
        if pred_geom is not None and not pred_geom.is_empty:
            for j in gt_sindex.intersection(pred_geom.bounds):
                score = iou(pred_geom, ground_truth_gdf.geometry.iloc[j])
                if score > best_iou:
                    best_iou = score
                    best_j = int(j)

        results.append(
            {
                "predicted_index": i,
                "matched_gt_index": best_j,
                "iou": best_iou,
                "is_match": best_iou >= iou_threshold,
            }
        )

    return results