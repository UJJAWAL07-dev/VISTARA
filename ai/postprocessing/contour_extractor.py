from typing import List, Dict, Any
import cv2
import numpy as np
from shapely.geometry import Polygon


class ContourExtractor:
    """Extracts, cleans, simplifies, and filters vector polygon geometries from raster masks."""

    def __init__(self, min_area: float = 40.0, max_area: float = 500000.0, tolerance: float = 1.5):
        self.min_area = min_area
        self.max_area = max_area
        self.tolerance = tolerance

    def extract_polygons(self, mask: np.ndarray, class_name: str) -> List[Dict[str, Any]]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        extracted = []

        for idx, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area < self.min_area or area > self.max_area:
                continue

            # Need at least 3 points to form a polygon
            if len(cnt) < 3:
                continue

            pts = cnt.squeeze(axis=1)
            if len(pts.shape) != 2 or pts.shape[0] < 3:
                continue

            poly = Polygon(pts)
            if not poly.is_valid:
                poly = poly.buffer(0)
            if poly.is_empty:
                continue

            # Douglas-Peucker simplification
            simplified_poly = poly.simplify(self.tolerance, preserve_topology=True)
            if simplified_poly.is_empty or simplified_poly.geom_type != "Polygon":
                continue

            extracted.append({
                "id": f"{class_name}_{idx + 1}",
                "class": class_name,
                "area_px": float(simplified_poly.area),
                "polygon": simplified_poly,
                "confidence": 0.85
            })

        return extracted