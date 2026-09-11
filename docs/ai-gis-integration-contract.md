# AI to GIS Integration Contract

This contract defines the spatial output interface between the AI/ML
module and the GIS engine. It is owned by Member 4 (GIS) for
coordination with Member 3 (AI).

## Accepted Inputs

Pass one of these shapes to `gis.layers.ai_output_to_layer()`:

1. A GeoJSON `FeatureCollection` dictionary:

   ```python
   {
       "type": "FeatureCollection",
       "features": [
           {
               "type": "Feature",
               "geometry": {...},
               "properties": {"class": "building", "confidence": 0.92},
           }
       ],
   }
   ```

2. A GeoPandas `GeoDataFrame`.

3. A list of records containing a Shapely geometry or GeoJSON geometry
   dictionary and optional properties:

   ```python
   [
       {
           "geometry": <shapely geometry or GeoJSON geometry dict>,
           "properties": {"class": "building", "confidence": 0.92},
       }
   ]
   ```

## CRS Requirement

The AI output must have a CRS, or the caller must provide `assume_crs`
when calling the adapter. `assume_crs` labels coordinates whose CRS is
known out-of-band; it does not transform them. The GIS engine never
guesses a CRS.

If the output is in pixel or normalized image coordinates, AI must also
provide the raster georeferencing needed to convert those coordinates to
real-world coordinates. Pixel-to-world conversion is a separate adapter
step and is not assumed here.

## Preserved Properties

Class labels, confidence scores, source IDs, and other useful properties
are retained through normalization and GeoJSON conversion.

## Processing Flow

```text
AI output
    |
    v
normalize_ai_output()       shape -> GeoDataFrame
    |
    v
explicit CRS assignment     assume_crs when needed
    |
    v
prepare_vector_layer()      optional AOI clip, reprojection, repair
    |
    v
GIS Layer                   metadata-rich output for backend/analysis/frontend
```

AI geometry repair defaults to enabled for `ai_output_to_layer()` and is
recorded in the resulting layer metadata. The adapter does not implement
or alter the AI model.

## Unsupported Formats

If the AI output uses a different format, do not rewrite the AI pipeline
just to match this contract. Add a focused adapter branch in
`gis/layers/ai_adapter.py` that converts the new format to a GeoDataFrame;
the existing preparation and Layer interfaces remain unchanged.
