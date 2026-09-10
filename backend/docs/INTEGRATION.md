# VISTARA Backend — Integration Guide (Phase 5)

This document is for teammates building the real **database**, **GIS**,
**GIS-analysis**, or **AI** implementations. It describes exactly what the
backend currently expects, so your work can plug in later without needing
to read the whole backend codebase.

**Nothing in this document is implemented yet on the database/GIS/AI side.**
This is a contract, not an announcement that integration has happened.

---

## 1. Current backend architecture

```
HTTP Request
  -> FastAPI Route            (app/routes/*.py)          - thin, no business logic
    -> Pydantic Schema        (app/schemas/*.py)         - request/response validation
      -> Service              (app/services/*.py)        - business logic
        -> Repository/Store   (in-memory today)          - persistence
        -> Integration Adapter (app/integrations/*.py)   - AI/GIS/Analysis calls (Processing only)
```

Every feature (Projects, Datasets, Processing/Jobs) follows this same
shape. Routes call a service; the service calls a repository (for
storage) and/or adapters (for the processing pipeline); nothing outside
the service layer touches storage or adapters directly.

**Current implementation status:** everything today is in-memory
(non-persistent, lost on restart) and every AI/GIS/Analysis call is a
deterministic mock. This document describes the *contracts* those real
implementations need to satisfy - not a claim that they exist.

---

## 2. Repository (storage) contracts

Defined as `typing.Protocol` classes in `app/core/interfaces.py`. A real
implementation (e.g. backed by PostgreSQL/PostGIS) must implement the same
methods with the same signatures - nothing else in the backend needs to
change if it does.

### `ProjectRepository`
```python
def add(self, project: Project) -> Project: ...
def get(self, project_id: str) -> Optional[Project]: ...
def list(self) -> List[Project]: ...
def update(self, project_id: str, project: Project) -> Optional[Project]: ...
def delete(self, project_id: str) -> bool: ...
```

### `DatasetRepository`
```python
def add(self, dataset: Dataset) -> Dataset: ...
def get(self, dataset_id: str) -> Optional[Dataset]: ...
def list(self, project_id: Optional[str] = None) -> List[Dataset]: ...
def update(self, dataset_id: str, dataset: Dataset) -> Optional[Dataset]: ...
def delete(self, dataset_id: str) -> bool: ...
```

### `JobRepository`
```python
def add(self, job: Job) -> Job: ...
def get(self, job_id: str) -> Optional[Job]: ...
def list(self) -> List[Job]: ...
def update(self, job_id: str, job: Job) -> Optional[Job]: ...
```
(No `delete()` - there's no delete-a-job endpoint today, so it's not part
of the contract. Add it later if that changes.)

`Project`, `Dataset`, and `Job` are plain dataclasses in `app/models/`.
A database-backed repository can return ORM objects instead, as long as
they expose the same attributes those dataclasses do (`id`, `name`,
`created_at`, etc.) - the service layer only reads attributes, it doesn't
care about the concrete type.

**How to connect a real repository later:** implement a class satisfying
the relevant Protocol (e.g. `PostgresProjectStore`), then pass an instance
of it into the corresponding service's constructor (e.g.
`ProjectService(store=PostgresProjectStore(...))`) at the point where the
service singleton is created. No route, schema, or business-logic code
needs to change.

---

## 3. AI / GIS / GIS-Analysis adapter contracts

Also defined in `app/core/interfaces.py`. These describe the processing
pipeline's three stages, orchestrated by `ProcessingService`
(`app/services/process_service.py`) in this order: AI -> GIS -> Analysis.

### `AIAdapterProtocol`
```python
def run_inference(self, job: Job) -> Dict[str, Any]: ...
```
**Input:** the `Job` object (has `.id`, `.project_id`, `.dataset_id`,
`.features` - a list like `["parcels", "buildings"]`).

**Output:** a GeoJSON `FeatureCollection` as a plain dict:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "buildings-001",
      "geometry": {"type": "Polygon", "coordinates": [[[lon, lat], ...]]},
      "properties": {"id": "buildings-001", "class": "buildings", "confidence": 0.9}
    }
  ]
}
```
The real AI repository currently exposes `ai.pipeline.VistaraAIPipeline`
with `process_image(image_path, output_path=None)`, which produces GeoJSON.
Converting that output into this exact shape is the real adapter's job -
the backend does not import or call `ai.pipeline` directly (and does not
today, on purpose - see §5).

### `GISAdapterProtocol`
```python
def process(self, job: Job, ai_result: Dict[str, Any]) -> Dict[str, Any]: ...
```
**Input:** the `Job` and the AI stage's `FeatureCollection` dict above.

**Output:**
```json
{
  "layer_id": "layer-<job-id>",
  "name": "Extracted features for job <job-id>",
  "crs": "EPSG:4326",
  "feature_count": 2,
  "geojson": { "...the FeatureCollection, possibly transformed..." }
}
```
The repository already exposes a stable facade at `gis.services` - a real
adapter should call *that*, not GIS internals (`gis.loaders`,
`gis.processing`, `gis.conversion`, `gis.layers`), so the GIS team can
change their internals freely without breaking this contract.

### `AnalysisAdapterProtocol`
```python
def analyze(self, job: Job, gis_result: Dict[str, Any]) -> Dict[str, Any]: ...
```
**Input:** the `Job` and the GIS stage's result dict above.

**Output:**
```json
{
  "statistics": {"feature_count": 2, "building_count": 1, "parcel_count": 1, "road_count": 0, "land_use_count": 0},
  "issues": [{"issue_id": "ISS-001", "type": "no_features_detected", "severity": "high"}],
  "validation": {"status": "valid", "confidence": 0.9}
}
```
There is currently no stable callable GIS-analysis service to call - this
is genuinely open for the GIS-analysis team to define.

**How to connect real adapters later:** implement a class satisfying the
relevant Protocol, then pass an instance of it into `ProcessingService`'s
constructor (`ai_adapter=`, `gis_adapter=`, `analysis_adapter=`) at the
point where the processing service singleton is created. Nothing in
`app/routes/process.py` or `app/schemas/process.py` needs to change,
since both were built around exactly the shapes above.

---

## 4. Expected inputs/outputs summary

See `app/schemas/process.py` for the full typed Pydantic definitions
(`GeoJSONFeatureCollection`, `GISResult`, `AnalysisResult`, `ProcessResult`)
that a completed job's API response conforms to - the shapes above are
the same shapes, just shown as plain JSON here for readability.

---

## 5. What is intentionally NOT implemented yet

- No database connection, ORM, schema, or migration of any kind. No
  SQLite, PostgreSQL, PostGIS, Redis, or any other storage engine.
- No import of, or call into, `/ai`, `/gis`, or `/gis-analysis` from
  anywhere in `/backend`. This is deliberate - those modules may not be
  ready or runnable, and the backend must work standalone until they are.
- No "real" adapter mode is implemented - `AI_MODE`/`GIS_MODE`/
  `ANALYSIS_MODE` exist as config, but setting any of them to anything
  other than `"mock"` currently raises a controlled error rather than
  calling real code (because that real code doesn't exist here yet).
- No background job processing / task queue - `ProcessingService` runs
  the pipeline synchronously. This may need to change once real AI/GIS
  calls are slow, but that's a future phase's concern, not this one.

---

## 6. How each team can integrate later

**Database team:** implement `ProjectRepository`, `DatasetRepository`,
`JobRepository` (from `app/core/interfaces.py`) backed by PostgreSQL/
PostGIS. Swap the store passed into each service's constructor. Nothing
else changes.

**GIS team:** implement `GISAdapterProtocol`, calling your `gis.services`
facade internally. Swap the adapter passed into `ProcessingService`.

**GIS-analysis team:** implement `AnalysisAdapterProtocol` once you have
a stable callable service to wrap. Swap the adapter passed into
`ProcessingService`.

**AI team:** implement `AIAdapterProtocol`, calling
`ai.pipeline.VistaraAIPipeline().process_image(...)` internally and
converting its output to the FeatureCollection shape above. Swap the
adapter passed into `ProcessingService`.

In every case: implement the Protocol, construct an instance of your
class, pass it into the relevant service's constructor. No changes to
routes, schemas, or orchestration logic are expected to be necessary.
