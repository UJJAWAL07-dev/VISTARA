"""
Integration contracts (Phase 5).

Pure typing - zero runtime behavior, zero new dependencies. These
Protocols exist so the swap point between "current in-memory/mock
implementation" and "future real implementation" is documented in
code, not just in docstrings scattered across service files.

Nothing here changes how the app runs today. Every existing store and
adapter already satisfies its corresponding Protocol - see
tests/test_interfaces.py for conformance checks that go beyond a bare
isinstance() check (which typing.Protocol supports but which does NOT
validate method signatures - only attribute/method *names* exist).

Storage contracts (ProjectRepository, DatasetRepository, JobRepository)
describe what a Phase 6+ PostgreSQL/PostGIS-backed store must
implement to be a drop-in replacement for the current
InMemoryXStore classes, without any service-layer changes.

Adapter contracts (AIAdapterProtocol, GISAdapterProtocol,
AnalysisAdapterProtocol) describe what a real AI/GIS/GIS-analysis
adapter must implement to replace the current mock adapters, without
any ProcessingService or route changes.

See backend/docs/INTEGRATION.md for the full integration guide aimed
at teammates implementing the real database/GIS/AI/GIS-analysis sides.
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from app.models.dataset import Dataset
from app.models.job import Job
from app.models.project import Project


@runtime_checkable
class ProjectRepository(Protocol):
    """Storage contract for Project persistence (see InMemoryProjectStore)."""

    def add(self, project: Project) -> Project: ...

    def get(self, project_id: str) -> Optional[Project]: ...

    def list(self) -> List[Project]: ...

    def update(self, project_id: str, project: Project) -> Optional[Project]: ...

    def delete(self, project_id: str) -> bool: ...


@runtime_checkable
class DatasetRepository(Protocol):
    """Storage contract for Dataset persistence (see InMemoryDatasetStore)."""

    def add(self, dataset: Dataset) -> Dataset: ...

    def get(self, dataset_id: str) -> Optional[Dataset]: ...

    def list(self, project_id: Optional[str] = None) -> List[Dataset]: ...

    def update(self, dataset_id: str, dataset: Dataset) -> Optional[Dataset]: ...

    def delete(self, dataset_id: str) -> bool: ...


@runtime_checkable
class JobRepository(Protocol):
    """Storage contract for Job persistence (see InMemoryJobStore).

    Note: the current InMemoryJobStore has no delete() - a future
    real store isn't required to add one either unless a delete
    endpoint is introduced. Kept out of this Protocol deliberately so
    the contract matches what actually exists today, not a
    speculative superset of it.
    """

    def add(self, job: Job) -> Job: ...

    def get(self, job_id: str) -> Optional[Job]: ...

    def list(self) -> List[Job]: ...

    def update(self, job_id: str, job: Job) -> Optional[Job]: ...


@runtime_checkable
class AIAdapterProtocol(Protocol):
    """
    Adapter contract for the AI feature-extraction stage (see AIAdapter).

    run_inference(job) -> a GeoJSON FeatureCollection (as a plain dict):
        {"type": "FeatureCollection", "features": [ ... ]}
    Each feature should have "type": "Feature", a "geometry" dict, and
    a "properties" dict (matching app.schemas.process.GeoJSONFeature).
    """

    def run_inference(self, job: Job) -> Dict[str, Any]: ...


@runtime_checkable
class GISAdapterProtocol(Protocol):
    """
    Adapter contract for the GIS normalization stage (see GISAdapter).

    process(job, ai_result) -> a normalized GIS-stage result:
        {"layer_id": str, "name": str, "crs": str,
         "feature_count": int, "geojson": <FeatureCollection dict>}
    (matching app.schemas.process.GISResult)
    """

    def process(self, job: Job, ai_result: Dict[str, Any]) -> Dict[str, Any]: ...


@runtime_checkable
class AnalysisAdapterProtocol(Protocol):
    """
    Adapter contract for the GIS-analysis stage (see AnalysisAdapter).

    analyze(job, gis_result) -> a structured analysis result:
        {"statistics": Dict[str, int],
         "issues": [{"issue_id": str, "type": str, "severity": str}, ...],
         "validation": {"status": str, "confidence": float}}
    (matching app.schemas.process.AnalysisResult)
    """

    def analyze(self, job: Job, gis_result: Dict[str, Any]) -> Dict[str, Any]: ...
