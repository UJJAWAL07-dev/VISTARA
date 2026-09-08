# VISTARA — AI/ML Subsystem

Responsible for feature extraction (building footprints and road corridors) from drone imagery and raster datasets, returning structured GeoJSON datasets for downstream GIS and backend consumption.

## Architecture & Workflow
1. **Preprocessing (`ai/preprocessing/`)**: Ingests `.tif`, `.png`, and `.jpg` imagery, validates dynamic ranges, and preserves geospatial affine transforms and coordinate reference systems.
2. **Inference (`ai/models/`, `ai/inference/`)**: Runs feature segmentation targeting building boundaries and road surfaces.
3. **Postprocessing (`ai/postprocessing/`)**: Extracts clean contours, simplifies boundaries using Douglas-Peucker algorithms, and converts coordinates into GeoJSON format.
4. **Pipeline Orchestrator (`ai/pipeline.py`)**: End-to-end interface for standalone execution or integration with `backend/app/services`.

## Installation
```powershell
pip install -r ai/requirements.txt