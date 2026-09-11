"""Assemble computed GIS analysis results into one layer report."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _compute_overall_status(
    business_rule_results: Optional[List[Dict[str, Any]]],
    scoring_results: Optional[Dict[str, Any]],
    pass_score_threshold: float,
) -> Optional[Dict[str, Any]]:
    """Derive a simple overall verdict from available rules and scoring."""
    if business_rule_results is None and scoring_results is None:
        return None

    reasons = []
    if business_rule_results:
        failed_rules = [
            result["rule"]
            for result in business_rule_results
            if not result.get("passed", True)
        ]
        if failed_rules:
            reasons.append(f"business rule(s) failed: {', '.join(failed_rules)}")

    if scoring_results and "mean_composite_score" in scoring_results:
        mean_score = scoring_results["mean_composite_score"]
        if mean_score < pass_score_threshold:
            reasons.append(
                f"mean composite score {mean_score} below threshold "
                f"{pass_score_threshold}"
            )

    return {"status": "PASS" if not reasons else "FAIL", "reasons": reasons}


def build_report(
    layer_name: str,
    business_rule_results: Optional[List[Dict[str, Any]]] = None,
    ai_validation_results: Optional[Dict[str, Any]] = None,
    statistics_results: Optional[Dict[str, Any]] = None,
    scoring_results: Optional[Dict[str, Any]] = None,
    landuse_results: Optional[Dict[str, Any]] = None,
    pass_score_threshold: float = 0.6,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble optional analysis results into a report for one layer."""
    overall = _compute_overall_status(
        business_rule_results, scoring_results, pass_score_threshold
    )

    return {
        "layer": layer_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validation": {
            "business_rules": business_rule_results,
            "ai_validation": ai_validation_results,
        },
        "statistics": statistics_results,
        "scoring": scoring_results,
        "landuse": landuse_results,
        "overall": overall,
        "metadata": extra_metadata or {},
    }