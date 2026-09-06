# Backend to GIS Integration Contract

Backend should import only from `gis.services`. The loader, processing,
conversion, and layer modules are internal GIS implementation details.

## Service Functions

| Function | Purpose | Returns |
|---|---|---|
| `list_sample_layers()` | List available sample files by category | dict of lists |
| `load_and_prepare_vector_layer(path, layer_id, name, ...)` | Load, validate, reproject, repair, and clip a vector file | `Layer` |
| `load_raster_layer(path, layer_id, name)` | Wrap a raster file without an open handle | `Layer` |
| `get_raster_metadata(path)` | Inspect raster metadata | dict |
| `get_layer_geojson(layer, target_crs="EPSG:4326")` | Convert a vector Layer for WebGIS output | GeoJSON dict |
| `export_layer_geojson_file(layer, out_path, ...)` | Export a vector Layer to GeoJSON | output path string |
| `ingest_ai_layer(ai_output, layer_id, name, ...)` | Convert AI output into a GIS-ready Layer | `Layer` |

## Error Handling

GIS service failures raise `GISEngineError` or one of its subclasses.
Backend should catch these exceptions and translate them into its own HTTP
responses. The GIS service layer does not define FastAPI routes or HTTP
status mappings.

Common errors include `FileNotFoundInGISError`, `UnsupportedFormatError`,
`VectorLoadError`, `RasterLoadError`, `MissingCRSError`, `ReprojectionError`,
`AOIError`, and `GeometryValidationError`.

## Layer Summaries

`Layer.summary()` returns a JSON-serializable metadata dictionary with the
layer ID, name, type, source, CRS, bounds, geometry types, feature count,
and processing metadata. Use it when an endpoint needs metadata without
returning full geometry.

## Example

```python
from gis.exceptions import GISEngineError
from gis.services import (
    get_layer_geojson,
    load_and_prepare_vector_layer,
)

try:
    layer = load_and_prepare_vector_layer(
        path="datasets/sample/parcels/parcels.geojson",
        layer_id="parcel_layer",
        name="Parcels",
        target_crs="EPSG:4326",
    )
    geojson = get_layer_geojson(layer)
except GISEngineError as error:
    # Translate the GIS error to the backend's HTTP response.
    ...
```
