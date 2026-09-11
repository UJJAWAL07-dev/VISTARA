from pathlib import Path
from typing import Dict
import cv2
import numpy as np
from ultralytics import YOLO


class PrototypeSegmentor:
    """
    Native Ultralytics YOLOv8 segmentation engine for VISTARA.
    Loads fine-tuned weights if available in ai/models/weights/best.pt,
    or falls back to the base yolov8n-seg.pt model.
    """

    def __init__(self, confidence_threshold: float = 0.25, model_weights: str = "yolov8n-seg.pt"):
        self.confidence_threshold = confidence_threshold

        # If a fine-tuned model exists in the weights folder, prioritize it
        custom_weights = Path("ai/models/weights/best.pt")
        if custom_weights.exists():
            print(f"Loading custom fine-tuned VISTARA model: {custom_weights}")
            self.model = YOLO(str(custom_weights))
        else:
            print(f"Loading base Ultralytics YOLO model: {model_weights}")
            self.model = YOLO(model_weights)

    def predict(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Runs YOLO segmentation and returns binary masks for target classes.
        """
        h, w = image.shape[:2]
        building_mask = np.zeros((h, w), dtype=np.uint8)
        road_mask = np.zeros((h, w), dtype=np.uint8)

        # Run inference using the YOLO engine
        results = self.model.predict(
            source=image,
            conf=self.confidence_threshold,
            retina_masks=True,
            verbose=False
        )

        if len(results) == 0 or results[0].masks is None:
            return {"building": building_mask, "road": road_mask}

        res = results[0]
        class_ids = res.boxes.cls.cpu().numpy().astype(int)
        names = res.names  # Mapping from class_id to label string
        masks = res.masks.data.cpu().numpy()

        for idx, mask in enumerate(masks):
            label = names[class_ids[idx]].lower()

            # Resize mask if dimensions differ from original image
            if mask.shape != (h, w):
                mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)

            mask_binary = (mask * 255).astype(np.uint8)

            # Route to the appropriate feature class
            if "building" in label or "house" in label or "roof" in label or "batiment" in label:
                building_mask = cv2.bitwise_or(building_mask, mask_binary)
            elif "road" in label or "street" in label or "path" in label:
                road_mask = cv2.bitwise_or(road_mask, mask_binary)
            else:
                # Default bucket for single-class datasets
                building_mask = cv2.bitwise_or(building_mask, mask_binary)

        return {
            "building": building_mask,
            "road": road_mask
        }