import asyncio
import logging

from app.core.config import settings
from app.workers.manager import WorkerManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info(f"Starting worker process with {settings.queue_workers} workers")
    manager = WorkerManager(num_workers=settings.queue_workers)
    asyncio.run(manager.run())


if __name__ == "__main__":
    main()
