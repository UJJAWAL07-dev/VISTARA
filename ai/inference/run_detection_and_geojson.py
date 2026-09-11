# Save this file as ai/inference/run_detection_and_geojson.py

from pathlib import Path
import cv2
import numpy as np
import geojson
from shapely.geometry import Polygon, mapping
from ai.models.segmentation_model import PrototypeSegmentor

def run_detection_pipeline():
    # 1. Initialize segmentor (loads custom fine-tuned weights automatically)
    segmentor = PrototypeSegmentor(confidence_threshold=0.3)
    
    # 2. Load sample image
    image_path = Path("ai/sample_data/image.png")
    if not image_path.exists():
        print(f"Error: Sample image not found at {image_path}")
        return
        
    image = cv2.imread(str(image_path))
    h, w = image.shape[:2]
    
    # 3. Run YOLOv8 inference
    print("Running YOLOv8 building segmentation inference...")
    predictions = segmentor.predict(image)
    building_mask = predictions["building"]
    
    # 4. Post-processing: Extract contours and convert masks to GeoJSON polygons
    contours, _ = cv2.findContours(building_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    features = []
    vis_image = image.copy()
    
    for contour in contours:
        if cv2.contourArea(contour) < 50:  # Filter out tiny noise
            continue
        
        points = contour.squeeze()
        if len(points.shape) < 2 or len(points) < 3:
            continue
            
        poly_coords = [[float(pt[0]), float(pt[1])] for pt in points]
        if poly_coords[0] != poly_coords[-1]:
            poly_coords.append(poly_coords[0])
            
        try:
            poly = Polygon(poly_coords)
            if not poly.is_valid:
                poly = poly.buffer(0)
            if poly.is_empty:
                continue
            
            # Draw green bounding contours on the visualization image
            cv2.drawContours(vis_image, [contour], -1, (0, 255, 0), 2)
            
            # Create GeoJSON feature contract
            feature = geojson.Feature(
                geometry=mapping(poly),
                properties={
                    "class": "building",
                    "confidence": 0.95,
                    "source": "VISTARA-AI-YOLOv8"
                }
            )
            features.append(feature)
        except Exception as e:
            continue
            
    feature_collection = geojson.FeatureCollection(features)
    
    # 5. Save outputs to disk
    output_dir = Path("ai/inference/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    out_image_path = output_dir / "detection_result.jpg"
    cv2.imwrite(str(out_image_path), vis_image)
    
    out_geojson_path = output_dir / "detections.geojson"
    with open(out_geojson_path, "w") as f:
        geojson.dump(feature_collection, f, indent=2)
        
    print(f"Detection complete!")
    print(f"-> Output visualization saved to: {out_image_path}")
    print(f"-> GeoJSON output saved to: {out_geojson_path}")
    print(f"-> Total building polygons extracted: {len(features)}")

if __name__ == "__main__":
    run_detection_pipeline()