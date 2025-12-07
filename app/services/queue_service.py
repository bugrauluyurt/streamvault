from datetime import datetime, timedelta

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import JobStatus, JobType
from app.models import Job


class QueueService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def enqueue(
        self,
        job_type: JobType,
        payload: dict | None = None,
        priority: int = 0,
        delay_seconds: int = 0,
    ) -> Job:
        scheduled_for = datetime.now()
        if delay_seconds > 0:
            scheduled_for = scheduled_for + timedelta(seconds=delay_seconds)

        job = Job(
            job_type=job_type,
            payload=payload or {},
            priority=priority,
            scheduled_for=scheduled_for,
        )
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def get_job(self, job_id: int) -> Job | None:
        stmt = select(Job).where(Job.id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_jobs(
        self,
        status: JobStatus | None = None,
        limit: int = 50,
    ) -> list[Job]:
        stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
        if status:
            stmt = stmt.where(Job.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def claim_job(self, worker_id: str) -> Job | None:
        claim_sql = text("""
            UPDATE jobs
            SET status = :processing,
                worker_id = :worker_id,
                started_at = now(),
                attempts = attempts + 1
            WHERE id = (
                SELECT id FROM jobs
                WHERE status = :pending
                  AND scheduled_for <= now()
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            RETURNING *
        """)

        result = await self.db.execute(
            claim_sql,
            {
                "processing": JobStatus.PROCESSING.value,
                "pending": JobStatus.PENDING.value,
                "worker_id": worker_id,
            },
        )
        row = result.fetchone()
        if row is None:
            return None

        stmt = select(Job).where(Job.id == row.id)
        job_result = await self.db.execute(stmt)
        return job_result.scalar_one()

    async def complete_job(self, job_id: int, result: dict | None = None) -> None:
        stmt = (
            update(Job)
            .where(Job.id == job_id)
            .values(
                status=JobStatus.COMPLETED,
                completed_at=datetime.now(),
                result=result or {},
            )
        )
        await self.db.execute(stmt)

    async def fail_job(self, job_id: int, error: str) -> None:
        job = await self.get_job(job_id)
        if job is None:
            return

        new_status = JobStatus.FAILED if job.attempts >= job.max_attempts else JobStatus.PENDING

        stmt = (
            update(Job)
            .where(Job.id == job_id)
            .values(
                status=new_status,
                error=error,
                worker_id=None,
            )
        )
        await self.db.execute(stmt)

    async def retry_job(self, job_id: int) -> None:
        stmt = (
            update(Job)
            .where(Job.id == job_id)
            .values(
                status=JobStatus.PENDING,
                attempts=0,
                error=None,
                worker_id=None,
                started_at=None,
                completed_at=None,
            )
        )
        await self.db.execute(stmt)
