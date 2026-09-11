"""Backend-facing facade for the GIS Analysis Engine."""

from typing import Any, Dict, List, Optional

import geopandas as gpd

from gis_analysis.config import IOU_MATCH_THRESHOLD, SCORE_WEIGHTS
from gis_analysis.landuse.area_breakdown import calculate_area_breakdown
from gis_analysis.landuse.classification_check import (
    check_classification_consistency,
    check_internal_classification_consistency,
)
from gis_analysis.reports.build_report import build_report
from gis_analysis.scoring.composite_score import score_layer
from gis_analysis.statistics.accuracy_metrics import calculate_accuracy_metrics
from gis_analysis.statistics.summary_stats import summarize_layer
from gis_analysis.validation.ai_validation import validate_against_ground_truth
from gis_analysis.validation.business_rules import check_contained_within, check_no_overlap


def run_business_rule_checks(
    gdf: gpd.GeoDataFrame,
    layer_name: str = "layer",
    check_overlap: bool = True,
    contained_within: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Run configured overlap and optional containment checks."""
    results = []
    if check_overlap:
        results.append(check_no_overlap(gdf, layer_name=layer_name))
    if contained_within is not None:
        results.append(
            check_contained_within(
                inner_gdf=contained_within["inner_gdf"],
                outer_gdf=gdf,
                inner_name=contained_within.get("inner_name", "inner_layer"),
                outer_name=contained_within.get("outer_name", layer_name),
            )
        )
    return results


def run_ai_validation(
    predicted_gdf: gpd.GeoDataFrame,
    ground_truth_gdf: gpd.GeoDataFrame,
    iou_threshold: float = IOU_MATCH_THRESHOLD,
    layer_name: str = "layer",
) -> Dict[str, Any]:
    """Run AI-to-ground-truth validation through the stable facade."""
    return validate_against_ground_truth(
        predicted_gdf, ground_truth_gdf, iou_threshold, layer_name
    )


def compute_accuracy_stats(ai_validation_report: Dict[str, Any]) -> Dict[str, Any]:
    """Compute accuracy metrics from an existing validation report."""
    return calculate_accuracy_metrics(ai_validation_report)


def compute_summary_stats(
    gdf: gpd.GeoDataFrame, layer_name: str = "layer"
) -> Dict[str, Any]:
    """Compute feature-count and area summary statistics."""
    return summarize_layer(gdf, layer_name=layer_name)


def compute_composite_scores(
    ai_validation_report: Dict[str, Any],
    ai_confidences: Optional[Dict[int, float]] = None,
    validity_report: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Compute per-feature and layer-level quality scores."""
    return score_layer(
        ai_validation_report,
        ai_confidences=ai_confidences,
        validity_report=validity_report,
        weights=weights or SCORE_WEIGHTS,
    )


def run_landuse_analysis(
    predicted_gdf: gpd.GeoDataFrame,
    ai_validation_report: Optional[Dict[str, Any]] = None,
    ground_truth_gdf: Optional[gpd.GeoDataFrame] = None,
    label_column: str = "land_use",
) -> Dict[str, Any]:
    """Run classification consistency and area breakdown analysis."""
    if ground_truth_gdf is not None and ai_validation_report is not None:
        classification = check_classification_consistency(
            predicted_gdf,
            ground_truth_gdf,
            ai_validation_report,
            label_column=label_column,
        )
        mode = "ground_truth"
    else:
        classification = check_internal_classification_consistency(
            predicted_gdf, label_column=label_column
        )
        mode = "internal"

    return {
        "classification": classification,
        "classification_mode": mode,
        "area_breakdown": calculate_area_breakdown(
            predicted_gdf, label_column=label_column
        ),
    }


def generate_full_report(
    layer_name: str,
    predicted_gdf: gpd.GeoDataFrame,
    ground_truth_gdf: Optional[gpd.GeoDataFrame] = None,
    validity_report: Optional[Dict[str, Any]] = None,
    ai_confidences: Optional[Dict[int, float]] = None,
    iou_threshold: float = IOU_MATCH_THRESHOLD,
    check_overlap: bool = True,
    contained_within: Optional[Dict[str, Any]] = None,
    run_landuse: bool = False,
    landuse_label_column: str = "land_use",
    pass_score_threshold: float = 0.6,
) -> Dict[str, Any]:
    """Run the end-to-end analysis pipeline and assemble one report."""
    business_rule_results = run_business_rule_checks(
        predicted_gdf,
        layer_name=layer_name,
        check_overlap=check_overlap,
        contained_within=contained_within,
    )

    ai_validation_results = None
    statistics_results = None
    scoring_results = None
    landuse_results = None

    if ground_truth_gdf is not None:
        ai_validation_results = run_ai_validation(
            predicted_gdf,
            ground_truth_gdf,
            iou_threshold=iou_threshold,
            layer_name=layer_name,
        )
        statistics_results = compute_accuracy_stats(ai_validation_results)
        scoring_results = compute_composite_scores(
            ai_validation_results,
            ai_confidences=ai_confidences,
            validity_report=validity_report,
        )

    if run_landuse:
        landuse_results = run_landuse_analysis(
            predicted_gdf,
            ai_validation_report=ai_validation_results,
            ground_truth_gdf=ground_truth_gdf,
            label_column=landuse_label_column,
        )

    return build_report(
        layer_name=layer_name,
        business_rule_results=business_rule_results,
        ai_validation_results=ai_validation_results,
        statistics_results=statistics_results,
        scoring_results=scoring_results,
        landuse_results=landuse_results,
        pass_score_threshold=pass_score_threshold,
    )