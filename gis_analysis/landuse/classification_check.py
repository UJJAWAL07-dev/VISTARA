"""Land-use classification consistency checks."""

from typing import Any, Dict, List

import geopandas as gpd

from gis_analysis.exceptions import InvalidInputError, ValidationRuleError
from gis_analysis.spatial.relationships import find_overlaps


def check_classification_consistency(
    predicted_gdf: gpd.GeoDataFrame,
    ground_truth_gdf: gpd.GeoDataFrame,
    ai_validation_report: Dict[str, Any],
    label_column: str = "land_use",
) -> Dict[str, Any]:
    """Compare labels for true-positive pairs in an existing report."""
    if label_column not in predicted_gdf.columns:
        raise InvalidInputError(f"'{label_column}' column not found in predicted_gdf")
    if label_column not in ground_truth_gdf.columns:
        raise InvalidInputError(f"'{label_column}' column not found in ground_truth_gdf")

    try:
        true_positives = ai_validation_report["true_positives"]
        disagreements: List[Dict[str, Any]] = []
        confusion: Dict[Any, Dict[Any, int]] = {}
        agree_count = 0
        for true_positive in true_positives:
            predicted_index = int(true_positive["predicted_index"])
            ground_truth_index = int(true_positive["matched_gt_index"])
            predicted_label = predicted_gdf[label_column].iloc[predicted_index]
            ground_truth_label = ground_truth_gdf[label_column].iloc[ground_truth_index]

            confusion.setdefault(ground_truth_label, {})
            confusion[ground_truth_label][predicted_label] = (
                confusion[ground_truth_label].get(predicted_label, 0) + 1
            )
            if predicted_label == ground_truth_label:
                agree_count += 1
            else:
                disagreements.append(
                    {
                        "predicted_index": predicted_index,
                        "gt_index": ground_truth_index,
                        "predicted_label": predicted_label,
                        "gt_label": ground_truth_label,
                    }
                )
    except (KeyError, IndexError, TypeError) as error:
        raise ValidationRuleError(
            "classification_consistency", f"malformed ai_validation_report: {error}"
        ) from error

    total_matched = len(true_positives)
    disagree_count = total_matched - agree_count
    return {
        "label_column": label_column,
        "total_matched": total_matched,
        "agree_count": agree_count,
        "disagree_count": disagree_count,
        "agreement_rate": round(agree_count / total_matched, 6)
        if total_matched > 0
        else 0.0,
        "disagreements": disagreements,
        "confusion": confusion,
    }


def check_internal_classification_consistency(
    gdf: gpd.GeoDataFrame,
    label_column: str = "land_use",
) -> Dict[str, Any]:
    """Find overlapping feature pairs with different land-use labels."""
    if label_column not in gdf.columns:
        raise InvalidInputError(f"'{label_column}' column not found in gdf")

    try:
        overlap_pairs = find_overlaps(gdf, layer_name="landuse_internal_check")
    except Exception as error:
        raise ValidationRuleError(
            "internal_classification_consistency", str(error)
        ) from error

    conflicts = []
    for first_index, second_index in overlap_pairs:
        label_a = gdf[label_column].iloc[first_index]
        label_b = gdf[label_column].iloc[second_index]
        if label_a != label_b:
            conflicts.append(
                {
                    "index_a": first_index,
                    "index_b": second_index,
                    "label_a": label_a,
                    "label_b": label_b,
                }
            )

    return {
        "label_column": label_column,
        "total_features": len(gdf),
        "overlap_pairs_checked": len(overlap_pairs),
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
    }