from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import ShowType
from app.models import Job, ScrapedPopularShow, ScrapedTopShow
from app.schemas.scrape import ScrapeShow
from app.services.scraper_service import ScraperService
from app.services.site_origins import get_site_origin


def _create_top_show_record(
    show: ScrapeShow, batch_sequence: int, show_type: ShowType
) -> ScrapedTopShow:
    return ScrapedTopShow(
        tmdb_id=show.tmdb_id,
        position=show.position or 0,
        show_type=show_type,
        batch_sequence=batch_sequence,
        details=show.model_dump(mode="json"),
    )


def _create_popular_show_record(
    show: ScrapeShow, batch_sequence: int, position: int
) -> ScrapedPopularShow:
    return ScrapedPopularShow(
        tmdb_id=show.tmdb_id,
        position=position,
        show_type=ShowType(show.show_type),
        batch_sequence=batch_sequence,
        details=show.model_dump(mode="json"),
    )


async def handle_scrape_top_ten(job: Job, db: AsyncSession) -> dict:
    origin_name = job.payload.get("origin", "justwatch")
    origin = get_site_origin(origin_name)

    batch_sequence = int(datetime.now().timestamp())
    counts = {"movies": 0, "series": 0}

    async def on_item_ready(show: ScrapeShow, show_type: str) -> None:
        st = ShowType.MOVIE if show_type == "movie" else ShowType.SERIES
        record = _create_top_show_record(show, batch_sequence, st)
        db.add(record)
        await db.flush()
        if show_type == "movie":
            counts["movies"] += 1
        else:
            counts["series"] += 1

    scraper = ScraperService()
    result = await scraper.extract_top_ten(origin=origin, on_item_ready=on_item_ready)

    if result is None:
        return {
            "date": date.today().isoformat(),
            "movies_count": 0,
            "series_count": 0,
        }

    return {
        "date": date.today().isoformat(),
        "movies_count": counts["movies"],
        "series_count": counts["series"],
        "batch_sequence": batch_sequence,
    }


async def handle_scrape_popular(job: Job, db: AsyncSession) -> dict:
    origin_name = job.payload.get("origin", "justwatch")
    url = job.payload.get("url")

    if not url:
        raise ValueError("url is required in payload")

    origin = get_site_origin(origin_name)

    max_items = job.payload.get("max_items", 50)
    download_tile_images = job.payload.get("download_tile_images", False)
    download_cast_images = job.payload.get("download_cast_images", False)
    download_background_images = job.payload.get("download_background_images", False)

    batch_sequence = int(datetime.now().timestamp())
    position_counter = {"value": 0}

    async def on_item_ready(show: ScrapeShow) -> None:
        position_counter["value"] += 1
        record = _create_popular_show_record(show, batch_sequence, position_counter["value"])
        db.add(record)
        await db.flush()

    scraper = ScraperService()
    result = await scraper.extract_with_origin_detailed(
        url=url,
        origin=origin,
        max_items=max_items,
        download_tile_images=download_tile_images,
        download_cast_images=download_cast_images,
        download_background_images=download_background_images,
        on_item_ready=on_item_ready,
    )

    return {
        "url": url,
        "shows_count": len(result.items),
        "batch_sequence": batch_sequence,
    }
