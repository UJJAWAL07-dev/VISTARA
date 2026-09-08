"""AI-vs-ground-truth validation for predicted spatial features."""

from typing import Any, Dict

import geopandas as gpd

from gis_analysis.config import IOU_MATCH_THRESHOLD
from gis_analysis.exceptions import ValidationRuleError
from gis_analysis.spatial.relationships import spatial_match


def validate_against_ground_truth(
    predicted_gdf: gpd.GeoDataFrame,
    ground_truth_gdf: gpd.GeoDataFrame,
    iou_threshold: float = IOU_MATCH_THRESHOLD,
    layer_name: str = "layer",
) -> Dict[str, Any]:
    """Classify predictions into true positives, false positives, and misses."""
    try:
        matches = spatial_match(
            predicted_gdf,
            ground_truth_gdf,
            iou_threshold,
            layer_name,
        )
    except Exception as error:
        raise ValidationRuleError("ai_ground_truth_match", str(error)) from error

    true_positives = []
    false_positives = []
    matched_gt_indices = set()
    for match in matches:
        if match["is_match"]:
            true_positives.append(
                {
                    "predicted_index": match["predicted_index"],
                    "matched_gt_index": match["matched_gt_index"],
                    "iou": match["iou"],
                }
            )
            matched_gt_indices.add(match["matched_gt_index"])
        else:
            false_positives.append(
                {
                    "predicted_index": match["predicted_index"],
                    "best_iou": match["iou"],
                }
            )

    false_negatives = sorted(set(range(len(ground_truth_gdf))) - matched_gt_indices)

    return {
        "layer": layer_name,
        "iou_threshold": iou_threshold,
        "total_predicted": len(predicted_gdf),
        "total_ground_truth": len(ground_truth_gdf),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "true_positive_count": len(true_positives),
        "false_positive_count": len(false_positives),
        "false_negative_count": len(false_negatives),
    }