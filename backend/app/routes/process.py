"""
Processing API routes.

Thin HTTP layer: Pydantic validates the request shape and feature
names, ProcessingService handles job creation/lookup, exceptions are
translated to HTTP responses here. No processing/orchestration logic
lives in this file - see process_service.py's `_dispatch_to_pipeline`
for where that connects later.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.process import JobStatusResponse, ProcessRequest, ProcessResponse
from app.services.process_service import (
    JobNotFoundError,
    ProcessingService,
    get_processing_service,
)

router = APIRouter(prefix="/process", tags=["processing"])


@router.post(
    "",
    response_model=ProcessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a processing request",
    description=(
        "Accepts a project/dataset reference and a list of features to extract "
        "(parcels, buildings, roads, land_use), creates a queued job, and returns "
        "its ID immediately. Actual feature extraction is orchestrated separately "
        "and is not performed synchronously by this endpoint."
    ),
)
async def create_process_job(
    payload: ProcessRequest,
    service: ProcessingService = Depends(get_processing_service),
) -> ProcessResponse:
    job = service.submit_job(payload)
    return ProcessResponse(job_id=job.id, status=job.status)


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Get the status of a processing job",
    responses={404: {"description": "Job not found"}},
)
async def get_process_job(
    job_id: str,
    service: ProcessingService = Depends(get_processing_service),
) -> JobStatusResponse:
    try:
        job = service.get_job(job_id)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return JobStatusResponse(job_id=job.id, status=job.status)
