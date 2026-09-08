from typing import Dict
import cv2
import numpy as np


class PrototypeSegmentor:
    """
    Lightweight, deterministic feature detector for prototype extraction
    of building footprints and linear road corridors.
    Works reliably without GPU or large external weights.
    """

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def predict(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Executes segmentation on RGB imagery.
        Returns:
            Dict mapping class_name -> binary mask [0, 255]
        """
        # Convert to HSV and Grayscale for contrast-based feature separation
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # 1. Building Footprints: High-contrast roofs / edge-dense structures
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh_building = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        building_mask = cv2.morphologyEx(thresh_building, cv2.MORPH_CLOSE, kernel)

        # 2. Roads: Low-saturation, uniform intensity asphalt corridors
        lower_gray = np.array([0, 0, 50])
        upper_gray = np.array([180, 50, 200])
        road_mask = cv2.inRange(hsv, lower_gray, upper_gray)
        road_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        road_mask = cv2.morphologyEx(road_mask, cv2.MORPH_OPEN, road_kernel)

        return {
            "building": building_mask,
            "road": road_mask
        }