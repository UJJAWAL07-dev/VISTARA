from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    DatasetDB,
    ProcessingJobDB,
    ProjectDB,
)
from app.models.dataset import Dataset
from app.models.job import Job
from app.models.project import Project


def _uuid(value: str) -> UUID:
    return UUID(value)


class PostgresProjectStore:
    def __init__(self, db: Session):
        self.db = db

    def add(self, project: Project) -> Project:
        row = ProjectDB(
            id=_uuid(project.id),
            name=project.name,
            description=project.description,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
        self.db.add(row)
        self.db.commit()
        return project

    def get(self, project_id: str) -> Optional[Project]:
        row = self.db.get(ProjectDB, _uuid(project_id))
        if row is None:
            return None
        return self._to_domain(row)

    def list(self) -> List[Project]:
        stmt = select(ProjectDB).order_by(ProjectDB.created_at)
        rows = self.db.scalars(stmt).all()
        return [self._to_domain(row) for row in rows]

    def update(self, project_id: str, project: Project) -> Optional[Project]:
        row = self.db.get(ProjectDB, _uuid(project_id))
        if row is None:
            return None

        row.name = project.name
        row.description = project.description
        row.status = project.status
        row.updated_at = project.updated_at

        self.db.commit()
        return project

    def delete(self, project_id: str) -> bool:
        row = self.db.get(ProjectDB, _uuid(project_id))
        if row is None:
            return False

        self.db.delete(row)
        self.db.commit()
        return True

    @staticmethod
    def _to_domain(row: ProjectDB) -> Project:
        return Project(
            id=str(row.id),
            name=row.name,
            description=row.description,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class PostgresDatasetStore:
    def __init__(self, db: Session):
        self.db = db

    def add(self, dataset: Dataset) -> Dataset:
        row = DatasetDB(
            id=_uuid(dataset.id),
            project_id=_uuid(dataset.project_id),
            name=dataset.name,
            dataset_type=dataset.dataset_type,
            description=dataset.description,
            status=dataset.status,
            file_path=getattr(dataset, "file_path", None),
            created_at=dataset.created_at,
            updated_at=dataset.updated_at,
        )

        self.db.add(row)
        self.db.commit()
        return dataset

    def get(self, dataset_id: str) -> Optional[Dataset]:
        row = self.db.get(DatasetDB, _uuid(dataset_id))
        if row is None:
            return None
        return self._to_domain(row)

    def list(self, project_id: Optional[str] = None) -> List[Dataset]:
        stmt = select(DatasetDB).order_by(DatasetDB.created_at)

        if project_id is not None:
            stmt = stmt.where(
                DatasetDB.project_id == _uuid(project_id)
            )

        rows = self.db.scalars(stmt).all()
        return [self._to_domain(row) for row in rows]

    def update(
        self,
        dataset_id: str,
        dataset: Dataset,
    ) -> Optional[Dataset]:
        row = self.db.get(DatasetDB, _uuid(dataset_id))
        if row is None:
            return None

        row.name = dataset.name
        row.dataset_type = dataset.dataset_type
        row.description = dataset.description
        row.status = dataset.status
        row.file_path = getattr(dataset, "file_path", None)
        row.updated_at = dataset.updated_at

        self.db.commit()
        return dataset

    def delete(self, dataset_id: str) -> bool:
        row = self.db.get(DatasetDB, _uuid(dataset_id))
        if row is None:
            return False

        self.db.delete(row)
        self.db.commit()
        return True

    def delete_by_project(self, project_id: str) -> int:
        rows = self.db.scalars(
            select(DatasetDB).where(
                DatasetDB.project_id == _uuid(project_id)
            )
        ).all()

        count = len(rows)

        for row in rows:
            self.db.delete(row)

        self.db.commit()
        return count

    @staticmethod
    def _to_domain(row: DatasetDB) -> Dataset:
        return Dataset(
            id=str(row.id),
            project_id=str(row.project_id),
            name=row.name,
            dataset_type=row.dataset_type,
            description=row.description,
            status=row.status,
            file_path=row.file_path,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class PostgresJobStore:
    def __init__(self, db: Session):
        self.db = db

    def add(self, job: Job) -> Job:
        row = ProcessingJobDB(
            id=_uuid(job.id),
            project_id=_uuid(job.project_id),
            dataset_id=_uuid(job.dataset_id),
            features=job.features,
            status=job.status,
            result=job.result,
            error=job.error,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

        self.db.add(row)
        self.db.commit()
        return job

    def get(self, job_id: str) -> Optional[Job]:
        row = self.db.get(ProcessingJobDB, _uuid(job_id))
        if row is None:
            return None

        return self._to_domain(row)

    def list(self) -> List[Job]:
        stmt = select(ProcessingJobDB).order_by(
            ProcessingJobDB.created_at
        )

        rows = self.db.scalars(stmt).all()
        return [self._to_domain(row) for row in rows]

    def update(
        self,
        job_id: str,
        job: Job,
    ) -> Optional[Job]:
        row = self.db.get(ProcessingJobDB, _uuid(job_id))
        if row is None:
            return None

        row.project_id = _uuid(job.project_id)
        row.dataset_id = _uuid(job.dataset_id)
        row.features = job.features
        row.status = job.status
        row.result = job.result
        row.error = job.error
        row.updated_at = job.updated_at

        self.db.commit()
        return job

    def delete(self, job_id: str) -> bool:
        row = self.db.get(ProcessingJobDB, _uuid(job_id))
        if row is None:
            return False

        self.db.delete(row)
        self.db.commit()
        return True

    @staticmethod
    def _to_domain(row: ProcessingJobDB) -> Job:
        return Job(
            id=str(row.id),
            project_id=str(row.project_id),
            dataset_id=str(row.dataset_id),
            features=list(row.features or []),
            status=row.status,
            result=row.result,
            error=row.error,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )