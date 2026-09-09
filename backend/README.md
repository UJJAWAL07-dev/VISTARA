# VISTARA Backend

FastAPI backend for the VISTARA project. Acts as an orchestrator: it accepts
requests from the frontend, coordinates the AI, GIS, and GIS-analysis
modules, and returns results. It does not implement AI, GIS, or
GIS-analysis algorithms itself.

## Status by phase

- **Phase 1** - FastAPI foundation, health check, CORS, configuration.
- **Phase 2** - Projects CRUD (`/api/v1/projects`).
- **Phase 3** - Datasets CRUD (`/api/v1/datasets`) and the Processing/Job
  Status API (`/api/v1/process`).
- **Phase 4** - Processing orchestration. `ProcessingService` now runs a
  job synchronously through three integration adapters and stores a
  structured result on the job.
- **Phase 5 (planned)** - Real PostgreSQL/PostGIS persistence, replacing
  the in-memory stores used by every phase so far.

## Phase 4: integration adapters

`app/integrations/` contains three adapters:

- `ai_adapter.py` - `AIAdapter.run_inference(job)`
- `gis_adapter.py` - `GISAdapter.process(job, ai_result)`
- `analysis_adapter.py` - `AnalysisAdapter.analyze(job, gis_result)`

`ProcessingService._dispatch_to_pipeline()` calls these three in sequence
and updates the job's status as it goes: `queued -> processing ->
completed` on success, or `-> failed` if any adapter raises.

**Current mode: mock only.** Every adapter's default (and currently only
implemented) mode returns deterministic, clearly-fake demo data - fixed
GeoJSON coordinates, fixed confidence scores. None of them import from or
execute the real `/ai`, `/gis`, or `/gis-analysis` modules. This is by
design for Phase 4: those modules aren't guaranteed to be ready or
runnable yet, so the backend must be demonstrable on its own.

**This is not a claim that AI/GIS/GIS-analysis are integrated.** The
orchestration boundary exists and works end-to-end; the actual
algorithms behind each adapter are placeholders.

### How real implementations will connect later

Each adapter takes a `mode` (`AI_MODE`, `GIS_MODE`, `ANALYSIS_MODE` in
`.env`, all defaulting to `mock`). A future real-mode branch inside each
adapter would call the real module - e.g. the AI adapter would call
`ai.pipeline.VistaraAIPipeline().process_image(...)` - and convert its
output to the same result shape the mock already returns. Because
`ProcessingService`, the routes, and the Pydantic schemas only depend on
that shape (not on how it was produced), swapping mock for real requires
no changes outside the relevant adapter file.

### Job result shape

A completed job's `GET /api/v1/process/{job_id}` response includes:

```json
{
  "job_id": "...",
  "status": "completed",
  "result": {
    "ai": { "type": "FeatureCollection", "features": [...] },
    "gis": { "layer_id": "...", "name": "...", "crs": "EPSG:4326", "feature_count": 4, "geojson": {...} },
    "analysis": { "statistics": {...}, "issues": [...], "validation": {...} }
  },
  "error": null
}
```

A failed job instead has `"status": "failed"`, `"result": null`, and a
short, safe `"error"` message - never a stack trace.

## Storage

Projects, Datasets, and Jobs are all held in isolated in-memory stores
(`InMemoryProjectStore`, `InMemoryDatasetStore`, `InMemoryJobStore`).
Nothing is persisted across a server restart. No SQLite, PostgreSQL,
Redis, or other infrastructure has been introduced - that's intentionally
deferred to Phase 5, which will replace these stores with a
PostgreSQL/PostGIS-backed implementation behind the same method
signatures.

## Running locally

```bash
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Docs: `http://127.0.0.1:8000/docs`

## Tests

```bash
python -m pytest -v
```
