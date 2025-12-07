from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums import ShowType
from app.models import ScrapedShow, ScrapedTopShow


class ShowsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_scraped_shows(
        self, skip: int = 0, limit: int = 20
    ) -> tuple[list[ScrapedShow], int]:
        count_stmt = select(func.count(ScrapedShow.id)).where(ScrapedShow.deleted_at.is_(None))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = (
            select(ScrapedShow)
            .where(ScrapedShow.deleted_at.is_(None))
            .order_by(ScrapedShow.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        shows = list(result.scalars().all())

        return shows, total

    async def get_scraped_show_by_id(self, show_id: int) -> ScrapedShow | None:
        stmt = select(ScrapedShow).where(
            ScrapedShow.id == show_id, ScrapedShow.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_top_ten_shows(self) -> tuple[list[ScrapedTopShow], list[ScrapedTopShow]]:
        latest_batch_stmt = select(func.max(ScrapedTopShow.batch_sequence))
        latest_batch_result = await self.db.execute(latest_batch_stmt)
        latest_batch = latest_batch_result.scalar_one_or_none()

        if latest_batch is None:
            return [], []

        movies_stmt = (
            select(ScrapedTopShow)
            .options(selectinload(ScrapedTopShow.show))
            .where(
                ScrapedTopShow.batch_sequence == latest_batch,
                ScrapedTopShow.show_type == ShowType.MOVIE,
            )
            .order_by(ScrapedTopShow.position)
            .limit(10)
        )
        movies_result = await self.db.execute(movies_stmt)
        movies = list(movies_result.scalars().all())

        series_stmt = (
            select(ScrapedTopShow)
            .options(selectinload(ScrapedTopShow.show))
            .where(
                ScrapedTopShow.batch_sequence == latest_batch,
                ScrapedTopShow.show_type == ShowType.SERIES,
            )
            .order_by(ScrapedTopShow.position)
            .limit(10)
        )
        series_result = await self.db.execute(series_stmt)
        series = list(series_result.scalars().all())

        return movies, series
