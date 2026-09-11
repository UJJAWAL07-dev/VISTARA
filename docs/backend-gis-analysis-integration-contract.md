# Backend and GIS Analysis Integration Contract

Backend should import analysis functionality only from `gis_analysis.services`.
The spatial, validation, statistics, scoring, land-use, and report modules are
internal implementation details.

```python
from gis_analysis.services import generate_full_report

report = generate_full_report(
    layer_name="parcels",
    predicted_gdf=ai_parcel_layer.data,
    ground_truth_gdf=ground_truth_layer.data,
    validity_report=ai_parcel_layer.metadata["validity_before_processing"],
    run_landuse=True,
)
```

All functions return JSON-serializable dictionaries/lists and raise an
`AnalysisError` subclass for invalid analysis inputs. GeoDataFrames must already
share a CRS; reprojection remains the responsibility of `gis.services`.