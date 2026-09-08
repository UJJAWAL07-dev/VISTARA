"""
Project business logic + storage.

Two things live here, deliberately kept separate:

1. InMemoryProjectStore - the ONLY place that touches the underlying
   dict. In Phase 5, this whole class gets swapped for a
   PostgresProjectStore backed by SQLAlchemy/PostGIS, implementing the
   same method signatures (create/get/list/update/delete). Nothing
   outside this class should ever reach into its internal dict.

2. ProjectService - business logic. Routes call this, never the store
   directly. This is what keeps app/routes/projects.py thin and what
   stays unchanged when the storage backend changes.

This module intentionally does not know anything about HTTP status
codes - it raises ProjectNotFoundError and lets the route layer
translate that into a 404.
"""

from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


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


class ProjectService:
    def __init__(self, store: Optional[InMemoryProjectStore] = None) -> None:
        self._store = store or InMemoryProjectStore()

    def create_project(self, data: ProjectCreate) -> Project:
        project = Project(name=data.name, description=data.description, status=data.status)
        return self._store.add(project)

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


# Module-level singleton store/service, shared across requests within
# this process. Swapped out entirely in Phase 5.
_default_service = ProjectService()


def get_project_service() -> ProjectService:
    """FastAPI dependency - swap this to inject a DB-backed service in Phase 5."""
    return _default_service
