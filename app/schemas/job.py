from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums import JobStatus, JobType


class JobCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_type: JobType
    payload: dict = {}
    priority: int = 0
    delay_seconds: int = 0


class JobResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    job_type: JobType
    status: JobStatus
    payload: dict
    priority: int
    attempts: int
    max_attempts: int
    result: dict | None
    error: str | None
    worker_id: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    scheduled_for: datetime


class JobListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[JobResponse]
