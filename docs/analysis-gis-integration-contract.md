# GIS Analysis Integration Contract

The GIS Analysis Engine (Member 5) consumes layers prepared by the GIS
engine. This contract defines what the analysis module can rely on. The GIS
engine does not implement scoring, validation rules, or statistics; those
responsibilities belong to `/gis-analysis`.

## Preparing a Bundle

Use `gis.services.prepare_layer_bundle()` when analysis needs multiple
related vector layers with one CRS and one spatial extent:

```python
from gis.services import (
    get_analysis_ready_bundle_summary,
    prepare_layer_bundle,
)

bundle = prepare_layer_bundle(
    layer_specs=[
        {
            "path": "datasets/sample/parcels/parcels.geojson",
            "layer_id": "parcel_layer",
            "name": "Parcels",
        },
        {
            "path": "datasets/sample/buildings/buildings.geojson",
            "layer_id": "building_layer",
            "name": "Buildings",
        },
    ],
    target_crs="EPSG:32643",
    aoi_bounds=(minx, miny, maxx, maxy),
    aoi_crs="EPSG:4326",
)

summary = get_analysis_ready_bundle_summary(bundle)
```

The result is `{layer_id: Layer}`. Pass the same `target_crs` and AOI
arguments to ensure cross-layer operations use a common CRS and extent.

## Guarantees and Checks

| Field | Meaning |
|---|---|
| `layer.crs` | Set when preparation succeeds; missing CRS raises `MissingCRSError`. |
| `summary["consistent_crs"]` | `True` only when every layer has the same CRS. Check before cross-layer operations. |
| `layer.metadata["validity_before_processing"]` | Validity report after clipping/reprojection and before optional repair. |
| `layer.metadata["repaired"]` | Whether repair was requested for that layer. Repair uses the heuristic `buffer(0)` and is best-effort. |
| `layer.metadata["clipped_to_aoi"]` | Whether a common AOI was applied. |
| `layer.data` | The prepared GeoDataFrame for vector operations. |

The analysis engine must still inspect `validity_before_processing` rather
than assuming every geometry is valid. It must also check `geometry_type`
and bounds because layers can contain different geometry types and extents.

## Cross-Layer Operations

When `consistent_crs` is `True`, standard GeoPandas/Shapely operations can be
used directly on the layer payloads:

```python
parcels = bundle["parcel_layer"].data
buildings = bundle["building_layer"].data
```

Do not silently reproject or repair layers inside `/gis-analysis`; request
those changes through the GIS service interface so all consumers share the
same tested behavior.
