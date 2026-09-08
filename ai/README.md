# VISTARA — AI/ML Subsystem

This module handles feature extraction (building footprints and road corridors) from drone imagery.

## 🚀 How to Run the Pipeline
The AI pipeline acts as a standalone service. You can run it via the CLI:
`python -m ai.pipeline <path_to_raster_image>`

## 📜 Integration Contract (Input / Output)

### INPUT
The AI module expects a path to a valid raster image (`.png`, `.jpg`, `.tif`).

### OUTPUT
The AI module outputs a standard **GeoJSON FeatureCollection** (`EPSG:4326`). 
The GIS and Backend teams must parse this GeoJSON for downstream analysis and database storage.

**Example Output Structure:**
{
  "type": "FeatureCollection",
  "properties": {
    "image_name": "synthetic_drone_view.png",
    "crs": "EPSG:4326",
    "total_features": 2
  },
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Polygon", "coordinates": [...] },
      "properties": {
        "id": "building_1",
        "class": "building",
        "confidence": 0.85,
        "area_px": 124.0
      }
    }
  ]
}