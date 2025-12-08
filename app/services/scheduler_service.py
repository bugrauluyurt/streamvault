import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import async_session_factory
from app.enums import JobType
from app.services.queue_service import QueueService

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()

    def _setup_jobs(self) -> None:
        self.scheduler.add_job(
            self._enqueue_job,
            CronTrigger(hour="6,15", minute=0),
            args=[JobType.SCRAPE_TOP_TEN, {}],
            id="scrape_top_ten",
        )
        self.scheduler.add_job(
            self._enqueue_job,
            CronTrigger(hour="6,15", minute=30),
            args=[JobType.SCRAPE_POPULAR, {"url": "https://www.justwatch.com/us/movies"}],
            id="scrape_popular_movies",
        )
        self.scheduler.add_job(
            self._enqueue_job,
            CronTrigger(hour="7,16", minute=0),
            args=[JobType.SCRAPE_POPULAR, {"url": "https://www.justwatch.com/us/tv-shows"}],
            id="scrape_popular_series",
        )
        self.scheduler.add_job(
            self._enqueue_job,
            CronTrigger(hour="7,16", minute=30),
            args=[JobType.VALIDATE_AND_STORE, {"source_table": "top_shows"}],
            id="validate_top_shows",
        )
        self.scheduler.add_job(
            self._enqueue_job,
            CronTrigger(hour="8,17", minute=0),
            args=[JobType.VALIDATE_AND_STORE, {"source_table": "popular_shows"}],
            id="validate_popular_shows",
        )

    async def _enqueue_job(self, job_type: JobType, payload: dict) -> None:
        try:
            async with async_session_factory() as session:
                queue = QueueService(session)
                job = await queue.enqueue(job_type, payload)
                await session.commit()
                logger.info("Scheduled job enqueued: %s (id=%s)", job_type.value, job.id)
        except Exception as e:
            logger.exception("Failed to enqueue scheduled job %s: %s", job_type.value, e)

    def start(self) -> None:
        self.scheduler.start()
        logger.info("Scheduler started with %d jobs", len(self.scheduler.get_jobs()))
        for job in self.scheduler.get_jobs():
            logger.info("  - %s: %s", job.id, job.trigger)

    def stop(self) -> None:
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
