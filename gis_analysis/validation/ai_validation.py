"""AI-generated feature validation against ground-truth geometries."""

from typing import Any, Dict

import geopandas as gpd

from gis_analysis.config import IOU_MATCH_THRESHOLD
from gis_analysis.spatial.relationships import spatial_match


def validate_ai_predictions(
    predicted_gdf: gpd.GeoDataFrame,
    ground_truth_gdf: gpd.GeoDataFrame,
    iou_threshold: float = IOU_MATCH_THRESHOLD,
    layer_name: str = "layer",
) -> Dict[str, Any]:
    """Return matched features, false positives, and false negatives.

    A ground-truth feature is considered detected only when it is selected
    as the best match and reaches the IoU threshold. This prevents a weak
    below-threshold overlap from hiding a missed ground-truth feature.
    """
    match_records = spatial_match(
        predicted_gdf,
        ground_truth_gdf,
        iou_threshold=iou_threshold,
        layer_name=layer_name,
    )
    matched = [record for record in match_records if record["is_match"]]
    unmatched_predicted = [record for record in match_records if not record["is_match"]]
    matched_ground_truth = {record["matched_gt_index"] for record in matched}
    unmatched_ground_truth = [
        {"ground_truth_index": index}
        for index in range(len(ground_truth_gdf))
        if index not in matched_ground_truth
    ]

    return {
        "layer": layer_name,
        "iou_threshold": iou_threshold,
        "valid": not unmatched_predicted and not unmatched_ground_truth,
        "predicted_count": len(predicted_gdf),
        "ground_truth_count": len(ground_truth_gdf),
        "matched_count": len(matched),
        "false_positive_count": len(unmatched_predicted),
        "false_negative_count": len(unmatched_ground_truth),
        "matched": matched,
        "unmatched_predicted": unmatched_predicted,
        "unmatched_ground_truth": unmatched_ground_truth,
    }