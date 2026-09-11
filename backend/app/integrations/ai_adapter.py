"""
VISTARA AI Adapter

Connects the FastAPI processing pipeline to the existing
VISTARA AI/ML pipeline in ../ai/pipeline.py.

Backend contract:
    run_inference(job) -> GeoJSON FeatureCollection
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import get_settings


class AIAdapterError(Exception):
    """Raised when the AI pipeline cannot complete inference."""


class AIAdapter:
    def __init__(self, mode: Optional[str] = None) -> None:
        self._mode = mode or get_settings().ai_mode

    def run_inference(self, job: Any) -> Dict[str, Any]:
        """
        Run the existing VISTARA AI pipeline and return its GeoJSON output.
        """

        if self._mode == "mock":
            raise AIAdapterError(
                "AI mode is 'mock'. Set VISTARA_AI_MODE=real before starting the backend."
            )

        if self._mode != "real":
            raise AIAdapterError(
                f"Unsupported AI mode: '{self._mode}'. Use 'real' or 'mock'."
            )

        try:
            # VISTARA root: backend/../
            vistara_root = Path(__file__).resolve().parents[3]
            ai_root = vistara_root / "ai"

            if not ai_root.exists():
                raise AIAdapterError(
                    f"AI module directory not found: {ai_root}"
                )

            # Make ../ai importable when FastAPI is started from backend/.
            root_str = str(vistara_root)
            if root_str not in sys.path:
                sys.path.insert(0, root_str)

            from ai.pipeline import VistaraAIPipeline

            # Current integration test image.
            image_path = (
                ai_root
                / "sample_data"
                / "synthetic_drone_view.png"
            )

            if not image_path.exists():
                raise AIAdapterError(
                    f"AI input image not found: {image_path}"
                )

            pipeline = VistaraAIPipeline()

            result = pipeline.process_image(str(image_path))

            if not isinstance(result, dict):
                raise AIAdapterError(
                    "AI pipeline returned an invalid result."
                )

            if result.get("type") != "FeatureCollection":
                raise AIAdapterError(
                    "AI pipeline did not return a GeoJSON FeatureCollection."
                )

            if "features" not in result:
                raise AIAdapterError(
                    "AI pipeline GeoJSON is missing 'features'."
                )

            return result

        except AIAdapterError:
            raise

        except Exception as exc:
            raise AIAdapterError(
                f"AI inference failed: {type(exc).__name__}: {exc}"
            ) from exc
