"""
Processing (job) business logic + storage.

Follows the same pattern as ProjectService/DatasetService:

1. InMemoryJobStore - the only place touching the underlying dict.
   Replaced wholesale in a later phase by a PostgreSQL-backed store
   with the same method signatures.

2. ProcessingService - business logic. Routes call this, never the
   store directly.

ORCHESTRATOR BOUNDARY: this service does NOT implement parcel
extraction, building/road/land-use detection, or any GIS algorithm.
`_dispatch_to_pipeline` is the single seam where that real work will
be wired in later (likely handed off to the AI/GIS services,
probably asynchronously, updating the job's status as it progresses).
For now it's a no-op - the job is simply created as "queued" and left
there, which is what the current spec asks for.

Note: project_id/dataset_id are NOT validated against the Projects/
Datasets stores in this phase (unlike Dataset -> Project validation
in Phase 3's dataset service). The processing request spec treats
them as opaque required strings. This can be tightened later if
cross-validation is wanted.
"""

from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional

from app.models.job import Job
from app.schemas.process import ProcessRequest


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
    def __init__(self, store: Optional[InMemoryJobStore] = None) -> None:
        self._store = store or InMemoryJobStore()

    def submit_job(self, data: ProcessRequest) -> Job:
        job = Job(
            project_id=data.project_id,
            dataset_id=data.dataset_id,
            features=list(data.features),
            status="queued",
        )
        self._store.add(job)
        self._dispatch_to_pipeline(job)
        return job

    def get_job(self, job_id: str) -> Job:
        job = self._store.get(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        return job

    def _dispatch_to_pipeline(self, job: Job) -> None:
        """
        Mocked integration seam.

        Later, this hands the job off to the AI/GIS/GIS-analysis
        pipeline (likely async) and updates job.status as processing
        progresses (queued -> processing -> completed/failed). For now
        it intentionally does nothing - the job stays "queued", per
        the current phase's scope (simulate the interface, not the
        algorithms).
        """
        return


# Module-level singleton, shared across requests within this process.
# Swapped out entirely once real persistence/orchestration land.
_default_service = ProcessingService()


def get_processing_service() -> ProcessingService:
    """FastAPI dependency - swap this to inject a DB-backed service later."""
    return _default_service
