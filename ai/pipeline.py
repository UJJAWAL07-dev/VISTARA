import json
from pathlib import Path
from typing import Dict, Any, Optional
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

    def process_image(self, image_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Runs the complete pipeline: Preprocessing -> Inference -> Postprocessing -> GeoJSON."""
        # 1. Load image and metadata
        image, metadata = self.loader.load(image_path)

        # 2. Predict features
        target_classes = self.config["pipeline"]["target_classes"]
        features = self.predictor.run(image, target_classes=target_classes)

        # 3. Convert to GeoJSON FeatureCollection
        geojson_result = self.converter.to_geojson(features, metadata)

        # 4. Optional file export
        if output_path:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w") as f:
                json.dump(geojson_result, f, indent=2)

        return geojson_result


if __name__ == "__main__":
    import sys
    pipeline = VistaraAIPipeline()
    sample_file = "datasets/sample/imagery/sample.png"
    out_file = "datasets/sample/sample_ai_output.geojson"
    
    target = sys.argv[1] if len(sys.argv) > 1 else sample_file
    if Path(target).exists():
        res = pipeline.process_image(target, out_file)
        print(f"Pipeline executed successfully. Extracted {res['properties']['total_features']} features.")
    else:
        print(f"Target '{target}' not found. Run pipeline with a valid raster path.")