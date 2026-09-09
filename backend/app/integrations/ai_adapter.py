"""
AI integration adapter (Phase 4).

Backend-facing interface between ProcessingService and the AI
feature-extraction step. Deliberately does NOT import anything from
`ai.*` at module level: the real AI repository (`ai.pipeline
.VistaraAIPipeline`, `process_image(image_path, output_path=None)`)
may not have its dependencies or data installed on every machine
running this backend, and importing it eagerly here would risk
crashing the whole API on startup for reasons outside this module's
control.

Phase 4 implements only the "mock" mode: deterministic, clearly-fake
GeoJSON output. It does NOT pretend to be the real model - values are
fixed demo coordinates near Bengaluru, not real detections.

Replacing this with the real AI pipeline later only means changing the
body of `_run_real` (or wherever the real call goes) to invoke
`ai.pipeline.VistaraAIPipeline().process_image(...)` and convert its
output to this same dict shape. ProcessingService, the routes, and the
Pydantic schemas do not need to change.
"""

from typing import Any, Dict, List, Optional

from app.core.config import get_settings


class AIAdapterError(Exception):
    """Raised when the AI stage fails. ProcessingService catches this and
    marks the job as failed with a safe message - never a raw traceback."""


# Fixed, clearly-fake demo coordinates (near Bengaluru) - one small
# polygon per supported feature type, so mock output is deterministic
# and repeatable for the same input.
_MOCK_GEOMETRIES: Dict[str, List[List[float]]] = {
    "buildings": [
        [77.5946, 12.9716], [77.5947, 12.9716],
        [77.5947, 12.9717], [77.5946, 12.9717], [77.5946, 12.9716],
    ],
    "roads": [
        [77.5950, 12.9720], [77.5955, 12.9720],
        [77.5955, 12.9722], [77.5950, 12.9722], [77.5950, 12.9720],
    ],
    "parcels": [
        [77.5940, 12.9710], [77.5948, 12.9710],
        [77.5948, 12.9718], [77.5940, 12.9718], [77.5940, 12.9710],
    ],
    "land_use": [
        [77.5935, 12.9705], [77.5943, 12.9705],
        [77.5943, 12.9713], [77.5935, 12.9713], [77.5935, 12.9705],
    ],
}


def _mock_feature(feature_id: str, feature_class: str, coordinates: List[List[float]]) -> Dict[str, Any]:
    return {
        "type": "Feature",
        "id": feature_id,
        "geometry": {"type": "Polygon", "coordinates": [coordinates]},
        "properties": {
            "id": feature_id,
            "class": feature_class,
            # Fixed demo confidence value - not a real model score.
            "confidence": 0.90,
        },
    }


class AIAdapter:
    def __init__(self, mode: Optional[str] = None) -> None:
        self._mode = mode or get_settings().ai_mode

    def run_inference(self, job: Any) -> Dict[str, Any]:
        """
        Returns a GeoJSON FeatureCollection (as a plain dict) representing
        extracted urban features for the requested `job.features`.
        """
        if self._mode != "mock":
            raise AIAdapterError(f"AI mode '{self._mode}' is not implemented in Phase 4.")
        return self._run_mock(job)

    def _run_mock(self, job: Any) -> Dict[str, Any]:
        features = []
        for index, feature_type in enumerate(job.features, start=1):
            coordinates = _MOCK_GEOMETRIES.get(feature_type, _MOCK_GEOMETRIES["parcels"])
            features.append(_mock_feature(f"{feature_type}-{index:03d}", feature_type, coordinates))
        return {"type": "FeatureCollection", "features": features}
