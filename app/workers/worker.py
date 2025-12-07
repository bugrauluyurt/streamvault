import asyncio
import logging
import time
import traceback
import uuid

from app.core.config import settings
from app.core.database import async_session_factory
from app.enums import JobType
from app.models import Job
from app.services.queue_service import QueueService
from app.workers.handlers import HANDLERS

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self, worker_id: str | None = None):
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self._stop_event = asyncio.Event()
        self._current_job: Job | None = None

    async def start(self) -> None:
        logger.info(
            f"[{self.worker_id}] Worker starting, polling every {settings.queue_poll_interval}s"
        )

        while not self._stop_event.is_set():
            try:
                async with async_session_factory() as session:
                    queue = QueueService(session)
                    job = await queue.claim_job(self.worker_id)

                    if job:
                        self._current_job = job
                        await self._process_job(job, queue)
                        self._current_job = None
                        await session.commit()
                    else:
                        await asyncio.sleep(settings.queue_poll_interval)

            except asyncio.CancelledError:
                logger.info(f"[{self.worker_id}] Worker cancelled")
                break
            except Exception as e:
                logger.exception(f"[{self.worker_id}] Unexpected error: {e}")
                await asyncio.sleep(settings.queue_poll_interval)

        logger.info(f"[{self.worker_id}] Worker stopped")

    async def _process_job(self, job: Job, queue: QueueService) -> None:
        job_type = JobType(job.job_type)
        handler = HANDLERS.get(job_type)

        if handler is None:
            await queue.fail_job(job.id, f"No handler for job type: {job_type}")
            logger.error(f"[{self.worker_id}] Job {job.id}: No handler for type '{job_type}'")
            return

        logger.info(
            f"[{self.worker_id}] Job {job.id}: Starting {job_type} "
            f"(attempt {job.attempts}/{job.max_attempts}, payload={job.payload})"
        )

        start_time = time.perf_counter()

        try:
            result = await handler(job)
            elapsed = time.perf_counter() - start_time
            await queue.complete_job(job.id, result)
            logger.info(
                f"[{self.worker_id}] Job {job.id}: Completed in {elapsed:.2f}s (result={result})"
            )
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            await queue.fail_job(job.id, error_msg)
            logger.error(
                f"[{self.worker_id}] Job {job.id}: Failed after {elapsed:.2f}s - "
                f"{type(e).__name__}: {e}"
            )

    def stop(self) -> None:
        self._stop_event.set()

    @property
    def is_processing(self) -> bool:
        return self._current_job is not None
