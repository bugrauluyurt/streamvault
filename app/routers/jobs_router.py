from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.enums import JobStatus
from app.schemas.job import JobCreate, JobListResponse, JobResponse
from app.services.queue_service import QueueService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
async def create_job(
    request: JobCreate,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    service = QueueService(db)
    job = await service.enqueue(
        job_type=request.job_type,
        payload=request.payload,
        priority=request.priority,
        delay_seconds=request.delay_seconds,
    )
    return JobResponse.model_validate(job)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status: JobStatus | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    service = QueueService(db)
    jobs = await service.get_jobs(status=status, limit=limit)
    return JobListResponse(items=[JobResponse.model_validate(job) for job in jobs])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    service = QueueService(db)
    job = await service.get_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse.model_validate(job)


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    service = QueueService(db)
    job = await service.get_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    await service.retry_job(job_id)
    job = await service.get_job(job_id)
    return JobResponse.model_validate(job)
