from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.repositories import PostgresDatasetStore
from app.schemas.dataset import DatasetCreate, DatasetResponse, DatasetUpdate
from app.services.dataset_service import DatasetNotFoundError, DatasetService
from app.services.project_service import ProjectNotFoundError

router = APIRouter(prefix="/datasets", tags=["datasets"])


def get_service(db: Session = Depends(get_db)) -> DatasetService:
    return DatasetService(store=PostgresDatasetStore(db))


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    payload: DatasetCreate,
    service: DatasetService = Depends(get_service),
) -> DatasetResponse:
    try:
        dataset = service.create_dataset(payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot create dataset: {exc}",
        ) from exc
    return DatasetResponse.model_validate(dataset)


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(
    project_id: Optional[str] = Query(default=None),
    service: DatasetService = Depends(get_service),
) -> List[DatasetResponse]:
    datasets = service.list_datasets(project_id=project_id)
    return [DatasetResponse.model_validate(d) for d in datasets]


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    service: DatasetService = Depends(get_service),
) -> DatasetResponse:
    try:
        dataset = service.get_dataset(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return DatasetResponse.model_validate(dataset)


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    payload: DatasetUpdate,
    service: DatasetService = Depends(get_service),
) -> DatasetResponse:
    try:
        dataset = service.update_dataset(dataset_id, payload)
    except DatasetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return DatasetResponse.model_validate(dataset)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    service: DatasetService = Depends(get_service),
) -> None:
    try:
        service.delete_dataset(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
