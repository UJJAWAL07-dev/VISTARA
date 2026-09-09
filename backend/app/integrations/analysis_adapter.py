"""
GIS Analysis integration adapter (Phase 4).

Backend-facing interface between ProcessingService and the analysis
stage. The real GIS Analysis module is not currently available as a
stable callable service, so this adapter does NOT import or invent one
- it implements a deterministic mock only.

This is DEMO/MOCK output. It does not represent the real GIS Analysis
engine's behavior, accuracy, or validation logic in any way.
"""

from typing import Any, Dict, List, Optional

from app.core.config import get_settings


class AnalysisAdapterError(Exception):
    """Raised when the analysis stage fails. ProcessingService catches this
    and marks the job as failed with a safe message - never a raw traceback."""


class AnalysisAdapter:
    def __init__(self, mode: Optional[str] = None) -> None:
        self._mode = mode or get_settings().analysis_mode

    def analyze(self, job: Any, gis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts the GIS-stage result and returns a structured (mock)
        analysis result: statistics, issues, validation.
        """
        if self._mode != "mock":
            raise AnalysisAdapterError(f"Analysis mode '{self._mode}' is not implemented in Phase 4.")
        return self._run_mock(job, gis_result)

    def _run_mock(self, job: Any, gis_result: Dict[str, Any]) -> Dict[str, Any]:
        features = gis_result.get("geojson", {}).get("features", [])

        counts: Dict[str, int] = {}
        for feature in features:
            feature_class = feature.get("properties", {}).get("class", "unknown")
            counts[feature_class] = counts.get(feature_class, 0) + 1

        statistics = {
            "feature_count": len(features),
            "building_count": counts.get("buildings", 0),
            "parcel_count": counts.get("parcels", 0),
            "road_count": counts.get("roads", 0),
            "land_use_count": counts.get("land_use", 0),
        }

        issues: List[Dict[str, Any]] = []
        if statistics["feature_count"] == 0:
            issues.append(
                {"issue_id": "ISS-001", "type": "no_features_detected", "severity": "high"}
            )

        validation = {
            "status": "valid" if not issues else "needs_review",
            # Fixed demo confidence value - not a real model/analysis score.
            "confidence": 0.90,
        }

        return {"statistics": statistics, "issues": issues, "validation": validation}
