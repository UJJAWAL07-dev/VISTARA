# VISTARA GIS Engine

The geospatial processing backbone for VISTARA. It loads, prepares,
converts, and manages vector and raster data for the backend, AI/ML
system, GIS Analysis Engine, and frontend WebGIS.

Owned by Member 4 (GIS Engine Engineer).

## Status: Phase 9 complete

1. Foundation: configuration, paths, CRS helpers, formats, exceptions
2. Loaders: vector/raster loading and metadata inspection
3. Conversion: CRS reprojection and GeoJSON generation
4. Layer management: consistent vector/raster Layer model and factories
5. Processing: validity checks, repair, AOI clipping, preparation pipeline
6. AI integration: flexible AI output adapter and CRS contract
7. Backend integration: stable `gis.services` facade
8. Analysis integration: consistent multi-layer bundles and summaries
9. Demo stabilization: tests, demo workflow, and this documentation

## Quick Start

From the repository root:

```bash
pip install -r gis/requirements.txt
pip install -r gis/requirements-dev.txt
python -m gis.demo_workflow
pytest gis/tests/ -v
```

The demo uses clearly labeled synthetic data and writes generated output to
`gis/_output/`. That directory is ignored by Git. Replace the synthetic
fixture paths with real files under `/datasets/sample` when they become
available; the downstream GIS service interfaces remain the same.

## Architecture

```text
gis/
├── config/          paths, CRS constants, supported formats
├── exceptions.py    typed GIS error hierarchy
├── loaders/         raw vector/raster loading and inspection
├── conversion/      CRS reprojection and GeoJSON conversion
├── layers/          Layer model, factories, AI adapter
├── processing/      validity, repair, clipping, preparation pipeline
├── services.py      stable backend/analysis integration facade
├── demo_workflow.py end-to-end synthetic demonstration
└── tests/           pytest suite using synthetic fixtures
```

Backend and analysis code should import from `gis.services`. The lower-level
modules are internal implementation details.

## Path Configuration

Paths are repository-relative and can be overridden with environment
variables:

| Variable | Default | Purpose |
|---|---|---|
| `VISTARA_DATASET_ROOT` | `<repo>/datasets/sample` | Read-only sample data root |
| `VISTARA_GIS_OUTPUT_ROOT` | `<repo>/gis/_output` | Generated GIS output root |
| `VISTARA_DEFAULT_PROJECTED_CRS` | unset | Optional projected CRS override |

## CRS Strategy

- Inspect CRS before spatial operations; never guess silently.
- Use EPSG:4326 for browser-facing GeoJSON by default.
- Use an appropriate projected CRS, usually a local UTM zone, for metric
  area, distance, and buffering operations.
- AOI clipping rejects mismatched CRS instead of silently transforming it.
- AI output without a CRS must provide explicit `assume_crs`.

## Supported Formats

- Vector: GeoJSON, ESRI Shapefile, GeoPackage
- Raster: GeoTIFF, JP2OpenJPEG, HFA (Erdas Imagine)

## Sample Data

The GIS engine reads, but does not own, this layout:

```text
datasets/sample/
├── parcels/
├── buildings/
├── roads/
├── land-use/
├── imagery/
├── dsm/
└── dtm/
```

Until official sample data is populated, `gis/loaders/synthetic_fixtures.py`
creates tiny test datasets under the ignored GIS output directory.

## Integration Contracts

- AI to GIS: [docs/ai-gis-integration-contract.md](../docs/ai-gis-integration-contract.md)
- Backend to GIS: [docs/backend-gis-integration-contract.md](../docs/backend-gis-integration-contract.md)
- GIS to Analysis: [docs/analysis-gis-integration-contract.md](../docs/analysis-gis-integration-contract.md)

## Error Handling

Service calls raise typed subclasses of `GISEngineError`, including
`FileNotFoundInGISError`, `UnsupportedFormatError`, `MissingCRSError`,
`ReprojectionError`, `GeometryValidationError`, `VectorLoadError`,
`RasterLoadError`, and `AOIError`. Backend maps these errors to HTTP
responses; the GIS engine does not define HTTP routes.

## Testing

The test suite covers vector/raster loading, metadata, CRS transformation,
GeoJSON conversion, geometry validation and repair, clipping, Layer metadata,
AI ingestion, service integration, and analysis bundle consistency.

```bash
pytest gis/tests/ -v
```

Tests use only synthetic fixtures and do not require real sample datasets.

## Ownership Boundaries

This engine does not implement:

- FastAPI or other HTTP routes (`/backend`)
- ML training or inference (`/ai`)
- Scoring, domain validation, or statistics (`/gis-analysis`)
- Database schema or persistence (`/database`)
