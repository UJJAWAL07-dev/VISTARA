"""
Project business logic + storage.

Two things live here, deliberately kept separate:

1. InMemoryProjectStore - the ONLY place that touches the underlying
   dict. In a future phase, this whole class gets swapped for a
   PostgresProjectStore backed by SQLAlchemy/PostGIS, implementing the
   ProjectRepository contract (see app/core/interfaces.py). Nothing
   outside this class should ever reach into its internal dict.

2. ProjectService - business logic. Routes call this, never the store
   directly. This is what keeps app/routes/projects.py thin and what
   stays unchanged when the storage backend changes.

This module intentionally does not know anything about HTTP status
codes - it raises ProjectNotFoundError and lets the route layer
translate that into a 404.

Phase 5: ProjectService now type-hints its `store` parameter against
the ProjectRepository Protocol instead of the concrete
InMemoryProjectStore class. This is a typing-only change - runtime
behavior is identical, since InMemoryProjectStore already satisfies
the Protocol (see tests/test_interfaces.py).

Phase 6: deleting a project now cascades to delete its datasets.
ProjectService never reaches into DatasetService's store directly -
it calls an injected `dataset_cleanup` callable, mirroring the same
pattern DatasetService already uses for its `project_lookup` callable
(see dataset_service.py). This keeps the two services decoupled: each
only knows about the other's public service method, never its
internal storage.
"""

import logging
from datetime import datetime, timezone
from threading import Lock
from typing import Callable, Dict, List, Optional

from app.core.interfaces import ProjectRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


class ProjectNotFoundError(Exception):
    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Project '{project_id}' not found")


class InMemoryProjectStore:
    """
    Isolated storage for Project objects.

    Not persisted across process restarts - this is a Phase 2
    prototype placeholder only, explicitly not intended to survive
    into later phases. A lock guards against race conditions between
    concurrent requests within a single process (FastAPI can run
    handlers concurrently even without multiple workers).
    """

    def __init__(self) -> None:
        self._projects: Dict[str, Project] = {}
        self._lock = Lock()

    def add(self, project: Project) -> Project:
        with self._lock:
            self._projects[project.id] = project
        return project

    def get(self, project_id: str) -> Optional[Project]:
        return self._projects.get(project_id)

    def list(self) -> List[Project]:
        return list(self._projects.values())

    def update(self, project_id: str, project: Project) -> Optional[Project]:
        with self._lock:
            if project_id not in self._projects:
                return None
            self._projects[project_id] = project
        return project

    def delete(self, project_id: str) -> bool:
        with self._lock:
            if project_id not in self._projects:
                return False
            del self._projects[project_id]
        return True


def _default_dataset_cleanup(project_id: str) -> int:
    """
    Default cascade-delete callable, used only when ProjectService isn't
    given an explicit `dataset_cleanup` (tests inject their own to keep
    stores isolated - see tests/test_projects.py).

    Imports app.services.dataset_service lazily, at call time rather than
    at module load time, specifically to avoid a circular import:
    dataset_service.py already imports get_project_service from this
    module (for its own `project_lookup` default), so importing
    dataset_service at the top of this file would create an import cycle.
    """
    from app.services.dataset_service import get_dataset_service

    return get_dataset_service().delete_by_project(project_id)


class ProjectService:
    def __init__(
        self,
        store: Optional[ProjectRepository] = None,
        dataset_cleanup: Optional[Callable[[str], int]] = None,
    ) -> None:
        self._store = store or InMemoryProjectStore()
        self._dataset_cleanup = dataset_cleanup or _default_dataset_cleanup

    def create_project(self, data: ProjectCreate) -> Project:
        project = Project(name=data.name, description=data.description, status=data.status)
        created = self._store.add(project)
        logger.info("Project %s created", created.id)
        return created

    def list_projects(self) -> List[Project]:
        return self._store.list()

    def get_project(self, project_id: str) -> Project:
        project = self._store.get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        return project

    def update_project(self, project_id: str, data: ProjectUpdate) -> Project:
        existing = self.get_project(project_id)  # raises ProjectNotFoundError if missing

        updates = data.model_dump(exclude_unset=True)
        for field_name, value in updates.items():
            setattr(existing, field_name, value)

        existing.updated_at = datetime.now(timezone.utc)

        updated = self._store.update(project_id, existing)
        if updated is None:
            raise ProjectNotFoundError(project_id)
        return updated

    def delete_project(self, project_id: str) -> None:
        deleted = self._store.delete(project_id)
        if not deleted:
            raise ProjectNotFoundError(project_id)

        removed_count = self._dataset_cleanup(project_id)
        logger.info("Project %s deleted (cascade removed %d dataset(s))", project_id, removed_count)


# Module-level singleton store/service, shared across requests within
# this process. Swapped out entirely in a future phase.
from app.db.database import SessionLocal
from app.db.repositories import PostgresProjectStore


def get_project_service() -> ProjectService:
    db = SessionLocal()
    try:
        return ProjectService(store=PostgresProjectStore(db))
    finally:
        db.close()