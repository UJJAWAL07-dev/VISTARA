import json
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np
import yaml

from ai.preprocessing.image_loader import ImageLoader
from ai.inference.predictor import Predictor
from ai.postprocessing.geo_converter import GeoConverter


class VistaraAIPipeline:
    """
    Main orchestration pipeline for Member 3 (AI/ML Subsystem).
    Exposes clean programmatic entry points for backend/GIS integration.
    """

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(Path(__file__).parent / "configs" / "default_config.yaml")

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.loader = ImageLoader()
        self.predictor = Predictor(
            confidence_threshold=self.config["model"]["confidence_threshold"],
            min_area=self.config["postprocessing"]["min_area_pixels"]
        )
        self.converter = GeoConverter()

    def process_image(
        self, 
        image_path: str, 
        output_geojson: Optional[str] = None,
        output_image: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs the pipeline: Preprocessing -> Inference -> Postprocessing -> GeoJSON + Preview Image."""
        # 1. Load image and metadata
        image, metadata = self.loader.load(image_path)

        # 2. Predict features (parcels/buildings & roads)
        target_classes = self.config["pipeline"]["target_classes"]
        features = self.predictor.run(image, target_classes=target_classes)

        # 3. Convert to GeoJSON FeatureCollection
        geojson_result = self.converter.to_geojson(features, metadata)

        # 4. Save GeoJSON if path provided
        if output_geojson:
            out_file = Path(output_geojson)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w") as f:
                json.dump(geojson_result, f, indent=2)

        # 5. Generate and Save Visual Output Image (Polygons overlay)
        if output_image:
            self._save_visual_overlay(image, features, output_image)

        return geojson_result

    @staticmethod
    def _save_visual_overlay(image: np.ndarray, features: list, output_path: str):
        """Draws semi-transparent polygon boundaries over the original image for visual inspection."""
        overlay = image.copy()
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Colors in BGR for OpenCV
        colors = {
            "building": (0, 255, 255),  # Yellow/Cyan parcels
            "road": (255, 0, 0)          # Blue road corridors
        }

        for feat in features:
            poly = feat["polygon"]
            pts = np.array(poly.exterior.coords, dtype=np.int32).reshape((-1, 1, 2))
            color = colors.get(feat["class"], (0, 255, 0))
            
            # Fill polygon lightly
            cv2.fillPoly(overlay, [pts], color)
            # Outline boundary sharply
            cv2.polylines(image, [pts], isClosed=True, color=(0, 0, 0), thickness=2)

        # Blend image and overlay for transparency
        annotated = cv2.addWeighted(overlay, 0.4, image, 0.6, 0)
        
        # Convert RGB to BGR for OpenCV saving
        cv2.imwrite(str(out_path), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
        print(f"Visual overlay saved to: {out_path}")


if __name__ == "__main__":
    import sys
    pipeline = VistaraAIPipeline()
    
    # Defaults
    default_input = "ai/sample_data/real_sample.jpeg"
    target_img = sys.argv[1] if len(sys.argv) > 1 else default_input
    
    out_geo = "ai/sample_data/output_parcels.geojson"
    out_img = "ai/sample_data/output_preview.png"

    if Path(target_img).exists():
        res = pipeline.process_image(target_img, output_geojson=out_geo, output_image=out_img)
        print(f"Pipeline executed successfully. Extracted {res['properties']['total_features']} features.")
    else:
        print(f"Target '{target_img}' not found. Please verify file path.")