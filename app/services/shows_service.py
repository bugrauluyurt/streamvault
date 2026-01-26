from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import ShowType, ValidationStatus
from app.models import ScrapedPopularShow, ScrapedShow, ScrapedTopShow


class ShowsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_popular_shows(
        self, show_type: ShowType, limit: int = 20, validated_only: bool = True
    ) -> list[ScrapedPopularShow]:
        latest_batch_stmt = select(func.max(ScrapedPopularShow.batch_sequence)).where(
            ScrapedPopularShow.show_type == show_type
        )
        latest_batch_result = await self.db.execute(latest_batch_stmt)
        latest_batch = latest_batch_result.scalar_one_or_none()

        if latest_batch is None:
            return []

        stmt = select(ScrapedPopularShow).where(
            ScrapedPopularShow.batch_sequence == latest_batch,
            ScrapedPopularShow.show_type == show_type,
        )

        # Only return validated items with TMDB IDs
        if validated_only:
            stmt = stmt.where(
                ScrapedPopularShow.tmdb_id.isnot(None),
                ScrapedPopularShow.validation_status.in_(
                    [
                        ValidationStatus.PROCESSED,
                        ValidationStatus.REPROCESSED,
                    ]
                ),
            )

        stmt = stmt.order_by(ScrapedPopularShow.position).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

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

    async def get_top_ten_shows(
        self, validated_only: bool = True
    ) -> tuple[list[ScrapedTopShow], list[ScrapedTopShow]]:
        latest_batch_stmt = select(func.max(ScrapedTopShow.batch_sequence))
        latest_batch_result = await self.db.execute(latest_batch_stmt)
        latest_batch = latest_batch_result.scalar_one_or_none()

        if latest_batch is None:
            return [], []

        movies_stmt = select(ScrapedTopShow).where(
            ScrapedTopShow.batch_sequence == latest_batch,
            ScrapedTopShow.show_type == ShowType.MOVIE,
        )
        if validated_only:
            movies_stmt = movies_stmt.where(
                ScrapedTopShow.tmdb_id.isnot(None),
                ScrapedTopShow.validation_status.in_(
                    [
                        ValidationStatus.PROCESSED,
                        ValidationStatus.REPROCESSED,
                    ]
                ),
            )
        movies_stmt = movies_stmt.order_by(ScrapedTopShow.position).limit(10)
        movies_result = await self.db.execute(movies_stmt)
        movies = list(movies_result.scalars().all())

        series_stmt = select(ScrapedTopShow).where(
            ScrapedTopShow.batch_sequence == latest_batch,
            ScrapedTopShow.show_type == ShowType.SERIES,
        )
        if validated_only:
            series_stmt = series_stmt.where(
                ScrapedTopShow.tmdb_id.isnot(None),
                ScrapedTopShow.validation_status.in_(
                    [
                        ValidationStatus.PROCESSED,
                        ValidationStatus.REPROCESSED,
                    ]
                ),
            )
        series_stmt = series_stmt.order_by(ScrapedTopShow.position).limit(10)
        series_result = await self.db.execute(series_stmt)
        series = list(series_result.scalars().all())

        return movies, series
