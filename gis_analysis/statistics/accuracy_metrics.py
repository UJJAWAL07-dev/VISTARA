"""Aggregate accuracy metrics derived from AI validation reports."""

from statistics import mean, median
from typing import Any, Dict, Optional

import geopandas as gpd

from gis_analysis.exceptions import InvalidInputError
from gis_analysis.spatial.crs_check import assert_consistent_crs
from gis_analysis.spatial.geometry_metrics import centroid_distance


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def calculate_accuracy_metrics(
    validation_report: Dict[str, Any],
    predicted_gdf: Optional[gpd.GeoDataFrame] = None,
    ground_truth_gdf: Optional[gpd.GeoDataFrame] = None,
) -> Dict[str, Any]:
    """Calculate classification, IoU, and optional positional metrics.

    ``validation_report`` must be produced by
    ``validate_against_ground_truth``. Centroid offsets are calculated only
    when both source GeoDataFrames are supplied; their units are the CRS units.
    """
    true_positive_count = int(validation_report["true_positive_count"])
    false_positive_count = int(validation_report["false_positive_count"])
    false_negative_count = int(validation_report["false_negative_count"])

    precision = _ratio(true_positive_count, true_positive_count + false_positive_count)
    recall = _ratio(true_positive_count, true_positive_count + false_negative_count)
    f1 = _ratio(2 * precision * recall, precision + recall)

    ious = [float(match["iou"]) for match in validation_report["true_positives"]]
    result: Dict[str, Any] = {
        "layer": validation_report.get("layer", "layer"),
        "iou_threshold": float(validation_report["iou_threshold"]),
        "true_positive_count": true_positive_count,
        "false_positive_count": false_positive_count,
        "false_negative_count": false_negative_count,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mean_iou": mean(ious) if ious else 0.0,
        "median_iou": median(ious) if ious else 0.0,
        "matched_iou_count": len(ious),
        "mean_centroid_offset": None,
        "median_centroid_offset": None,
        "max_centroid_offset": None,
    }

    if (predicted_gdf is None) != (ground_truth_gdf is None):
        raise InvalidInputError(
            "predicted_gdf and ground_truth_gdf must be supplied together"
        )
    if predicted_gdf is None or ground_truth_gdf is None:
        return result

    assert_consistent_crs(predicted_gdf, ground_truth_gdf, context="accuracy_metrics")
    offsets = [
        centroid_distance(
            predicted_gdf.geometry.iloc[match["predicted_index"]],
            ground_truth_gdf.geometry.iloc[match["matched_gt_index"]],
        )
        for match in validation_report["true_positives"]
    ]
    if offsets:
        result["mean_centroid_offset"] = mean(offsets)
        result["median_centroid_offset"] = median(offsets)
        result["max_centroid_offset"] = max(offsets)

    return result