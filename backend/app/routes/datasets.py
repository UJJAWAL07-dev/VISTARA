"""
Datasets API routes.

Same thin-HTTP-layer pattern as Projects: validation via Pydantic
schemas, all logic delegated to DatasetService, exceptions translated
to HTTP responses here. Creating a dataset with a nonexistent
project_id surfaces as 404 (via ProjectNotFoundError), the same as a
request for a dataset that doesn't exist (via DatasetNotFoundError).
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.dataset import DatasetCreate, DatasetResponse, DatasetUpdate
from app.services.dataset_service import (
    DatasetNotFoundError,
    DatasetService,
    get_dataset_service,
)
from app.services.project_service import ProjectNotFoundError

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post(
    "",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new dataset under a project",
    responses={404: {"description": "Parent project not found"}},
)
async def create_dataset(
    payload: DatasetCreate,
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetResponse:
    try:
        dataset = service.create_dataset(payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot create dataset: {exc}",
        ) from exc
    return DatasetResponse.model_validate(dataset)


@router.get(
    "",
    response_model=List[DatasetResponse],
    summary="List datasets, optionally filtered by project",
)
async def list_datasets(
    project_id: Optional[str] = Query(default=None, description="Filter datasets by project ID"),
    service: DatasetService = Depends(get_dataset_service),
) -> List[DatasetResponse]:
    datasets = service.list_datasets(project_id=project_id)
    return [DatasetResponse.model_validate(d) for d in datasets]


@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
    summary="Get a single dataset by ID",
    responses={404: {"description": "Dataset not found"}},
)
async def get_dataset(
    dataset_id: str,
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetResponse:
    try:
        dataset = service.get_dataset(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DatasetResponse.model_validate(dataset)


@router.put(
    "/{dataset_id}",
    response_model=DatasetResponse,
    summary="Update an existing dataset",
    responses={404: {"description": "Dataset not found"}},
)
async def update_dataset(
    dataset_id: str,
    payload: DatasetUpdate,
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetResponse:
    try:
        dataset = service.update_dataset(dataset_id, payload)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DatasetResponse.model_validate(dataset)


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a dataset",
    responses={404: {"description": "Dataset not found"}},
)
async def delete_dataset(
    dataset_id: str,
    service: DatasetService = Depends(get_dataset_service),
) -> None:
    try:
        service.delete_dataset(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
