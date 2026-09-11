"""
Processing API routes.

Thin HTTP layer: Pydantic validates the request shape and feature
names, ProcessingService handles job creation and orchestration,
exceptions are translated to HTTP responses here. No orchestration
logic lives in this file - see process_service.py's
`_dispatch_to_pipeline` for the AI -> GIS -> Analysis flow.

Phase 6: added GET /process (list all jobs), mirroring the existing
list-endpoint convention already used by Projects and Datasets.

Phase 9: create_process_job now also catches ProjectNotFoundError and
DatasetNotFoundError, translating them to 404 exactly like every other
NotFoundError in the app already is. This is required because
ProcessingService.submit_job now validates the referenced project and
dataset actually exist (see process_service.py) - without this catch,
those errors would instead reach the global exception handler in
main.py and produce an opaque 500, not the 404 the API contract needs.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.process import JobStatusResponse, ProcessRequest, ProcessResponse
from app.services.dataset_service import DatasetNotFoundError
from app.services.process_service import (
    JobNotFoundError,
    ProcessingService,
    get_processing_service,
)
from app.services.project_service import ProjectNotFoundError

router = APIRouter(prefix="/process", tags=["processing"])


@router.post(
    "",
    response_model=ProcessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a processing request",
    description=(
        "Accepts a project/dataset reference and a list of features to extract "
        "(parcels, buildings, roads, land_use), creates a job, and synchronously "
        "runs it through the (currently mocked) AI -> GIS -> Analysis pipeline "
        "before returning. The returned status reflects the outcome at return "
        "time (queued/processing/completed/failed) - use GET /process/{job_id} "
        "to re-check status and retrieve the full result later."
    ),
    responses={404: {"description": "Referenced project or dataset not found"}},
)
async def create_process_job(
    payload: ProcessRequest,
    service: ProcessingService = Depends(get_processing_service),
) -> ProcessResponse:
    try:
        job = service.submit_job(payload)
    except (JobNotFoundError, ProjectNotFoundError, DatasetNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ProcessResponse(job_id=job.id, status=job.status)


@router.get(
    "",
    response_model=List[JobStatusResponse],
    summary="List all processing jobs",
)
async def list_process_jobs(
    service: ProcessingService = Depends(get_processing_service),
) -> List[JobStatusResponse]:
    jobs = service.list_jobs()
    return [
        JobStatusResponse(job_id=job.id, status=job.status, result=job.result, error=job.error)
        for job in jobs
    ]


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
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        result=job.result,
        error=job.error,
    )
