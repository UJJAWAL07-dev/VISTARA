from pathlib import Path
from ultralytics import YOLO

def run_training():
    print("Initializing VISTARA YOLOv8 Segmentation Training...")
    
    # Load baseline lightweight YOLOv8 nano segmentation model
    model = YOLO("yolov8n-seg.pt")
    
    # Resolve absolute path to data.yaml from project root
    data_yaml = Path("datasets/sample/cadastral_data/data.yaml").resolve()
    output_dir = Path("ai/models/weights")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Start fine-tuning
    model.train(
        data=str(data_yaml),
        epochs=30,           # 30 epochs for a fast prototype training run
        imgsz=640,           # Standard YOLO input dimension
        batch=4,             # Safe batch size for CPU/modest hardware
        project=str(output_dir),
        name="vistara_run",
        exist_ok=True
    )
    
    print(f"Training complete! Best weights saved to: {output_dir}/vistara_run/weights/best.pt")

if __name__ == "__main__":
    run_training()