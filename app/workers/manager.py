import asyncio
import logging
import signal

from app.core.config import settings
from app.workers.worker import Worker

logger = logging.getLogger(__name__)


class WorkerManager:
    def __init__(self, num_workers: int | None = None):
        self.num_workers = num_workers or settings.queue_workers
        self.workers: list[Worker] = []
        self._tasks: list[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        logger.info(f"Starting {self.num_workers} workers...")

        for i in range(self.num_workers):
            worker = Worker(worker_id=f"worker-{i + 1}")
            self.workers.append(worker)
            task = asyncio.create_task(worker.start())
            self._tasks.append(task)

        logger.info(f"All {self.num_workers} workers started")

    async def stop(self, timeout: float = 30.0) -> None:
        logger.info("Stopping workers...")

        for worker in self.workers:
            worker.stop()

        if self._tasks:
            done, pending = await asyncio.wait(
                self._tasks,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED,
            )

            for task in pending:
                task.cancel()

            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

        logger.info("All workers stopped")

    async def run(self) -> None:
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._handle_signal)

        await self.start()

        await self._shutdown_event.wait()

        await self.stop()

    def _handle_signal(self) -> None:
        logger.info("Received shutdown signal")
        self._shutdown_event.set()
