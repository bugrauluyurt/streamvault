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
        self._tasks: list[asyncio.Task[None]] = []
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        logger.info(f"[Manager] Starting {self.num_workers} worker(s)...")

        for i in range(self.num_workers):
            worker = Worker(worker_id=f"worker-{i + 1}")
            self.workers.append(worker)
            task = asyncio.create_task(worker.start())
            self._tasks.append(task)

        logger.info(f"[Manager] All {self.num_workers} worker(s) started and polling for jobs")

    async def stop(self, timeout: float = 30.0) -> None:
        logger.info("[Manager] Initiating graceful shutdown...")

        for worker in self.workers:
            worker.stop()

        if self._tasks:
            logger.info(f"[Manager] Waiting up to {timeout}s for workers to finish current jobs...")
            _, pending = await asyncio.wait(
                self._tasks,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED,
            )

            if pending:
                logger.warning(f"[Manager] {len(pending)} worker(s) still running, forcing cancel")
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)

        logger.info("[Manager] All workers stopped, shutdown complete")

    async def run(self) -> None:
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._handle_signal)

        logger.info("[Manager] Worker manager initialized, press Ctrl+C to stop")
        await self.start()

        await self._shutdown_event.wait()

        await self.stop()

    def _handle_signal(self) -> None:
        logger.info("[Manager] Received shutdown signal (SIGINT/SIGTERM)")
        self._shutdown_event.set()
