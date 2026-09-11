@'
import logging
from datetime import datetime, timezone
from typing import Callable, Optional, List

from sqlalchemy.orm import Session

from app.db.repositories import PostgresDatasetStore
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.services.project_service import get_project_service, ProjectNotFoundError

logger = logging.getLogger(__name__)


class DatasetNotFoundError(Exception):
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        super().__init__(f"Dataset '{dataset_id}' not found")


class DatasetService:
    def __init__(
        self,
        store=None,
        project_lookup: Optional[Callable[[str], object]] = None,
    ) -> None:
        self._store = store
        self._project_lookup = (
            project_lookup or get_project_service().get_project
        )

    def create_dataset(self, data: DatasetCreate) -> Dataset:
        if self._store is None:
            raise RuntimeError("DatasetService database store is not configured")

        self._project_lookup(data.project_id)

        dataset = Dataset(
            project_id=data.project_id,
            name=data.name,
            dataset_type=data.dataset_type,
            description=data.description,
            status=data.status,
            file_path=getattr(data, "file_path", None),
        )

        created = self._store.add(dataset)

        logger.info(
            "Dataset %s created under project %s",
            created.id,
            created.project_id,
        )

        return created

    def list_datasets(self, project_id: Optional[str] = None) -> List[Dataset]:
        return self._store.list(project_id=project_id)

    def get_dataset(self, dataset_id: str) -> Dataset:
        dataset = self._store.get(dataset_id)

        if dataset is None:
            raise DatasetNotFoundError(dataset_id)

        return dataset

    def update_dataset(
        self,
        dataset_id: str,
        data: DatasetUpdate,
    ) -> Dataset:
        existing = self.get_dataset(dataset_id)

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

        logger.info("Dataset %s deleted", dataset_id)

    def delete_by_project(self, project_id: str) -> int:
        datasets = self._store.list(project_id=project_id)

        for dataset in datasets:
            self._store.delete(dataset.id)

        return len(datasets)


def get_dataset_service(db: Session) -> DatasetService:
    return DatasetService(
        store=PostgresDatasetStore(db),
    )
'@ | Set-Content -Encoding UTF8 app\services\dataset_service.py