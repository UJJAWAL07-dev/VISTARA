from typing import Dict, Any, List
import numpy as np
from ai.models.segmentation_model import PrototypeSegmentor
from ai.postprocessing.contour_extractor import ContourExtractor


class Predictor:
    """Inference runner bridging model inference and polygon extraction."""

    def __init__(self, confidence_threshold: float = 0.5, min_area: float = 40.0):
        self.model = PrototypeSegmentor(confidence_threshold=confidence_threshold)
        self.extractor = ContourExtractor(min_area=min_area)

    def run(self, image: np.ndarray, target_classes: List[str]) -> List[Dict[str, Any]]:
        masks = self.model.predict(image)
        all_features = []

        for class_name in target_classes:
            if class_name in masks:
                polys = self.extractor.extract_polygons(masks[class_name], class_name)
                all_features.extend(polys)

        return all_features