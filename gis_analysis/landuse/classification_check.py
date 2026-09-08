"""Land-use label consistency checks."""

from typing import Any, Dict, Optional

import geopandas as gpd

from gis_analysis.exceptions import InvalidInputError
from gis_analysis.spatial.relationships import find_overlaps


def _label(value: Any) -> str:
    return "unknown" if value is None else str(value)


def check_classification_consistency(
    predicted_gdf: gpd.GeoDataFrame,
    ground_truth_gdf: Optional[gpd.GeoDataFrame] = None,
    validation_report: Optional[Dict[str, Any]] = None,
    predicted_label_column: str = "land_use",
    ground_truth_label_column: Optional[str] = None,
) -> Dict[str, Any]:
    """Compare predicted land-use labels for matched features.

    When ground truth is unavailable, the function checks for overlapping
    predicted polygons with contradictory labels instead.
    """
    if predicted_label_column not in predicted_gdf.columns:
        raise InvalidInputError(f"missing predicted label column '{predicted_label_column}'")

    if ground_truth_gdf is None:
        return check_internal_classification_consistency(
            predicted_gdf, predicted_label_column
        )
    if validation_report is None:
        raise InvalidInputError("validation_report is required when ground truth is provided")
    ground_truth_label_column = ground_truth_label_column or predicted_label_column
    if ground_truth_label_column not in ground_truth_gdf.columns:
        raise InvalidInputError(
            f"missing ground-truth label column '{ground_truth_label_column}'"
        )

    matches = []
    confusion_matrix: Dict[str, Dict[str, int]] = {}
    for true_positive in validation_report.get("true_positives", []):
        predicted_index = int(true_positive["predicted_index"])
        ground_truth_index = int(true_positive["matched_gt_index"])
        predicted_label = _label(predicted_gdf.iloc[predicted_index][predicted_label_column])
        ground_truth_label = _label(
            ground_truth_gdf.iloc[ground_truth_index][ground_truth_label_column]
        )
        confusion_matrix.setdefault(ground_truth_label, {})
        confusion_matrix[ground_truth_label][predicted_label] = (
            confusion_matrix[ground_truth_label].get(predicted_label, 0) + 1
        )
        matches.append(
            {
                "predicted_index": predicted_index,
                "ground_truth_index": ground_truth_index,
                "predicted_label": predicted_label,
                "ground_truth_label": ground_truth_label,
                "is_consistent": predicted_label == ground_truth_label,
                "iou": float(true_positive["iou"]),
            }
        )

    consistent_count = sum(match["is_consistent"] for match in matches)
    return {
        "mode": "ground_truth",
        "predicted_label_column": predicted_label_column,
        "ground_truth_label_column": ground_truth_label_column,
        "matched_count": len(matches),
        "consistent_count": consistent_count,
        "inconsistent_count": len(matches) - consistent_count,
        "consistency_rate": consistent_count / len(matches) if matches else 0.0,
        "matches": matches,
        "confusion_matrix": confusion_matrix,
    }


def check_internal_classification_consistency(
    gdf: gpd.GeoDataFrame,
    label_column: str = "land_use",
) -> Dict[str, Any]:
    """Find overlapping polygons with contradictory land-use labels."""
    if label_column not in gdf.columns:
        raise InvalidInputError(f"missing label column '{label_column}'")

    conflicts = []
    for first_index, second_index in find_overlaps(gdf, layer_name="land_use"):
        first_label = _label(gdf.iloc[first_index][label_column])
        second_label = _label(gdf.iloc[second_index][label_column])
        if first_label != second_label:
            conflicts.append(
                {
                    "feature_index_a": first_index,
                    "feature_index_b": second_index,
                    "label_a": first_label,
                    "label_b": second_label,
                }
            )

    return {
        "mode": "internal",
        "label_column": label_column,
        "checked_count": len(gdf),
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "passed": not conflicts,
    }