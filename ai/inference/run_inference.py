from pathlib import Path
import cv2
from ai.models.segmentation_model import PrototypeSegmentor

def run_sample_inference():
    # Initialize segmentor (automatically loads ai/models/weights/best.pt)
    segmentor = PrototypeSegmentor(confidence_threshold=0.3)

    # Define path to your sample test image
    image_path = Path("ai/sample_data/real_sample.jpeg")
    if not image_path.exists():
        print(f"Sample image not found at {image_path}. Please update the path.")
        return

    image = cv2.imread(str(image_path))
    if image is None:
        print("Failed to read image file with OpenCV.")
        return

    print("Running YOLOv8 segmentation inference...")
    predictions = segmentor.predict(image)

    print("Inference completed successfully!")
    print(f"Building mask pixels detected: {(predictions['building'] > 0).sum()}")
    print(f"Road mask pixels detected: {(predictions['road'] > 0).sum()}")

if __name__ == "__main__":
    run_sample_inference()