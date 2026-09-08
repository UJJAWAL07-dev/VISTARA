"""
Dataset business logic + storage.

Mirrors the Projects pattern from Phase 2 exactly:

1. InMemoryDatasetStore - the only place touching the underlying dict.
   Replaced wholesale in Phase 5 by a PostgreSQL/PostGIS-backed store
   with the same method signatures.

2. DatasetService - business logic. Routes call this, never the store
   directly.

The one addition versus Projects: every dataset must reference an
existing project. Rather than importing InMemoryProjectStore directly
(which would couple the two stores together), DatasetService takes a
`project_lookup` callable - supplied at construction time from the
existing ProjectService.get_project - so validation reuses Phase 2's
ProjectNotFoundError without either service reaching into the other's
storage.
"""

from datetime import datetime, timezone
from threading import Lock
from typing import Callable, Dict, List, Optional

from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.services.project_service import get_project_service


class DatasetNotFoundError(Exception):
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        super().__init__(f"Dataset '{dataset_id}' not found")


class InMemoryDatasetStore:
    """Isolated storage for Dataset objects. Not persisted across restarts."""

    def __init__(self) -> None:
        self._datasets: Dict[str, Dataset] = {}
        self._lock = Lock()

    def add(self, dataset: Dataset) -> Dataset:
        with self._lock:
            self._datasets[dataset.id] = dataset
        return dataset

    def get(self, dataset_id: str) -> Optional[Dataset]:
        return self._datasets.get(dataset_id)

    def list(self, project_id: Optional[str] = None) -> List[Dataset]:
        values = list(self._datasets.values())
        if project_id is not None:
            values = [d for d in values if d.project_id == project_id]
        return values

    def update(self, dataset_id: str, dataset: Dataset) -> Optional[Dataset]:
        with self._lock:
            if dataset_id not in self._datasets:
                return None
            self._datasets[dataset_id] = dataset
        return dataset

    def delete(self, dataset_id: str) -> bool:
        with self._lock:
            if dataset_id not in self._datasets:
                return False
            del self._datasets[dataset_id]
        return True


class DatasetService:
    def __init__(
        self,
        store: Optional[InMemoryDatasetStore] = None,
        project_lookup: Optional[Callable[[str], object]] = None,
    ) -> None:
        self._store = store or InMemoryDatasetStore()
        # Defaults to the shared Phase 2 ProjectService's get_project method,
        # which already raises ProjectNotFoundError when the ID is missing.
        self._project_lookup = project_lookup or get_project_service().get_project

    def create_dataset(self, data: DatasetCreate) -> Dataset:
        self._project_lookup(data.project_id)  # raises ProjectNotFoundError if missing
        dataset = Dataset(
            project_id=data.project_id,
            name=data.name,
            dataset_type=data.dataset_type,
            description=data.description,
            status=data.status,
        )
        return self._store.add(dataset)

    def list_datasets(self, project_id: Optional[str] = None) -> List[Dataset]:
        return self._store.list(project_id=project_id)

    def get_dataset(self, dataset_id: str) -> Dataset:
        dataset = self._store.get(dataset_id)
        if dataset is None:
            raise DatasetNotFoundError(dataset_id)
        return dataset

    def update_dataset(self, dataset_id: str, data: DatasetUpdate) -> Dataset:
        existing = self.get_dataset(dataset_id)  # raises DatasetNotFoundError if missing

        updates = data.model_dump(exclude_unset=True)
        for field_name, value in updates.items():
            setattr(existing, field_name, value)

        existing.updated_at = datetime.now(timezone.utc)

        updated = self._store.update(dataset_id, existing)
        if updated is None:
            raise DatasetNotFoundError(dataset_id)
        return updated

    def delete_dataset(self, dataset_id: str) -> None:
        deleted = self._store.delete(dataset_id)
        if not deleted:
            raise DatasetNotFoundError(dataset_id)


# Module-level singleton, shared across requests within this process.
# Swapped out entirely in Phase 5.
_default_service = DatasetService()


def get_dataset_service() -> DatasetService:
    """FastAPI dependency - swap this to inject a DB-backed service in Phase 5."""
    return _default_service
