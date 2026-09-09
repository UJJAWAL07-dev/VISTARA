"""
GIS integration adapter (Phase 4).

Backend-facing interface between ProcessingService and the GIS stage.
Does NOT implement any real GIS algorithm and does NOT import GIS
internals (`gis.loaders`, `gis.processing`, `gis.conversion`,
`gis.layers`). The repository already exposes a stable facade at
`gis.services` - when a real GIS implementation is ready, that facade
is what a future version of this adapter should call, not the
internal modules.

Phase 4 implements only the "mock" mode: it takes the AI stage's
GeoJSON FeatureCollection and wraps it into a normalized GIS-stage
result shape, without altering the geometry/features in any
meaningful way. This is intentionally trivial - it exists so
ProcessingService and downstream schemas have a stable shape to work
with regardless of what the real GIS stage eventually does internally.
"""

from typing import Any, Dict, Optional

from app.core.config import get_settings


class GISAdapterError(Exception):
    """Raised when the GIS stage fails. ProcessingService catches this and
    marks the job as failed with a safe message - never a raw traceback."""


class GISAdapter:
    def __init__(self, mode: Optional[str] = None) -> None:
        self._mode = mode or get_settings().gis_mode

    def process(self, job: Any, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts the AI stage's GeoJSON FeatureCollection and returns a
        normalized GIS-stage result: layer_id, name, crs, feature_count,
        geojson.
        """
        if self._mode != "mock":
            raise GISAdapterError(f"GIS mode '{self._mode}' is not implemented in Phase 4.")
        return self._run_mock(job, ai_result)

    def _run_mock(self, job: Any, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        features = ai_result.get("features", [])
        return {
            "layer_id": f"layer-{job.id}",
            "name": f"Extracted features for job {job.id}",
            "crs": "EPSG:4326",
            "feature_count": len(features),
            "geojson": ai_result,
        }
