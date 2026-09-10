"""
Processing (job) business logic + storage.

Follows the same pattern as ProjectService/DatasetService:

1. InMemoryJobStore - the only place touching the underlying dict.
   Replaced wholesale in a later phase by a PostgreSQL-backed store
   with the same method signatures.

2. ProcessingService - business logic. Routes call this, never the
   store directly.

PHASE 4 ORCHESTRATION: `_dispatch_to_pipeline` (kept as the original
seam name from Phase 3) now actually orchestrates the AI -> GIS ->
Analysis adapters, synchronously, and updates the job's status as it
goes: queued -> processing -> completed/failed. This is still not a
real AI/GIS/GIS-analysis implementation - the adapters injected here
default to deterministic mocks (see app/integrations/). Swapping in
real adapters later requires no change to this orchestration logic,
only to what `AIAdapter`/`GISAdapter`/`AnalysisAdapter` do internally.

Any adapter failure is caught here: the job is marked "failed" with a
safe, human-readable error message, and the exception never propagates
out of this method - the API process must never crash because a mock
(or, later, a real) adapter raised.

Note: project_id/dataset_id are NOT validated against the Projects/
Datasets stores in this phase (unlike Dataset -> Project validation
in Phase 3's dataset service). The processing request spec treats
them as opaque required strings. This can be tightened later if
cross-validation is wanted.

Phase 5: ProcessingService now type-hints its `store` and adapter
parameters against the JobRepository / AIAdapterProtocol /
GISAdapterProtocol / AnalysisAdapterProtocol Protocols (see
app/core/interfaces.py) instead of the concrete classes. Typing-only
change - no behavior change; the concrete mock classes are still the
runtime defaults.

Phase 6: added `list_jobs()` (backing the new GET /api/v1/process list
endpoint) and lifecycle logging (job created/completed/failed).
"""

import logging
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional

from app.core.interfaces import (
    AIAdapterProtocol,
    AnalysisAdapterProtocol,
    GISAdapterProtocol,
    JobRepository,
)
from app.integrations.ai_adapter import AIAdapter, AIAdapterError
from app.integrations.analysis_adapter import AnalysisAdapter, AnalysisAdapterError
from app.integrations.gis_adapter import GISAdapter, GISAdapterError
from app.models.job import Job
from app.schemas.process import ProcessRequest

logger = logging.getLogger(__name__)


class JobNotFoundError(Exception):
    def __init__(self, job_id: str):
        self.job_id = job_id
        super().__init__(f"Job '{job_id}' not found")


class InMemoryJobStore:
    """Isolated storage for Job objects. Not persisted across restarts."""

    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._lock = Lock()

    def add(self, job: Job) -> Job:
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def list(self) -> List[Job]:
        return list(self._jobs.values())

    def update(self, job_id: str, job: Job) -> Optional[Job]:
        with self._lock:
            if job_id not in self._jobs:
                return None
            self._jobs[job_id] = job
        return job


class ProcessingService:
    def __init__(
        self,
        store: Optional[JobRepository] = None,
        ai_adapter: Optional[AIAdapterProtocol] = None,
        gis_adapter: Optional[GISAdapterProtocol] = None,
        analysis_adapter: Optional[AnalysisAdapterProtocol] = None,
    ) -> None:
        self._store = store or InMemoryJobStore()
        # Adapters are injectable so tests (and later, real
        # implementations) can swap them without touching this class.
        self._ai_adapter = ai_adapter or AIAdapter()
        self._gis_adapter = gis_adapter or GISAdapter()
        self._analysis_adapter = analysis_adapter or AnalysisAdapter()

    def submit_job(self, data: ProcessRequest) -> Job:
        job = Job(
            project_id=data.project_id,
            dataset_id=data.dataset_id,
            features=list(data.features),
            status="queued",
        )
        self._store.add(job)
        logger.info("Job %s created (project=%s, dataset=%s, features=%s)",
                    job.id, job.project_id, job.dataset_id, job.features)
        self._dispatch_to_pipeline(job)
        return job

    def list_jobs(self) -> List[Job]:
        return self._store.list()

    def get_job(self, job_id: str) -> Job:
        job = self._store.get(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        return job

    def _dispatch_to_pipeline(self, job: Job) -> None:
        """
        Orchestrates AI -> GIS -> Analysis for the given job, synchronously.

        On success: job.result = {"ai": ..., "gis": ..., "analysis": ...},
        job.status = "completed".

        On any adapter failure: job.error is set to a short, safe message
        (never the exception's raw traceback), job.status = "failed", and
        this method returns normally - it never lets an exception escape,
        so a broken adapter can never crash the API process.
        """
        self._set_status(job, "processing")

        try:
            ai_result = self._ai_adapter.run_inference(job)
            gis_result = self._gis_adapter.process(job, ai_result)
            analysis_result = self._analysis_adapter.analyze(job, gis_result)
        except (AIAdapterError, GISAdapterError, AnalysisAdapterError) as exc:
            job.error = str(exc)
            self._set_status(job, "failed")
            logger.warning("Job %s failed: %s", job.id, job.error)
            return
        except Exception:
            # Defensive: an adapter should only ever raise its own XAdapterError,
            # but if something unexpected happens, fail safely rather than
            # exposing internal details or crashing the request.
            job.error = "Processing failed due to an unexpected internal error."
            self._set_status(job, "failed")
            logger.exception("Job %s failed with an unexpected error", job.id)
            return

        job.result = {"ai": ai_result, "gis": gis_result, "analysis": analysis_result}
        self._set_status(job, "completed")
        logger.info("Job %s completed", job.id)

    def _set_status(self, job: Job, new_status: str) -> None:
        job.status = new_status
        job.updated_at = datetime.now(timezone.utc)
        self._store.update(job.id, job)


# Module-level singleton, shared across requests within this process.
# Swapped out entirely once real persistence/orchestration land.
_default_service = ProcessingService()


def get_processing_service() -> ProcessingService:
    """FastAPI dependency - swap this to inject a DB-backed service later."""
    return _default_service
