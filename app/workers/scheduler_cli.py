import asyncio
import logging
import signal

from app.services.scheduler_service import SchedulerService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def run_scheduler() -> None:
    logger.info("Starting scheduler process")
    scheduler = SchedulerService()
    scheduler.start()

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()

    logger.info("Shutdown signal received")
    scheduler.stop()
    logger.info("Scheduler process stopped")


def main() -> None:
    asyncio.run(run_scheduler())


if __name__ == "__main__":
    main()
