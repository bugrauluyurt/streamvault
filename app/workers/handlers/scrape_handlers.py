from datetime import date

from app.models import Job
from app.services.scraper_service import ScraperService
from app.services.site_origins import get_site_origin


async def handle_scrape_top_ten(job: Job) -> dict:
    origin_name = job.payload.get("origin", "justwatch")
    origin = get_site_origin(origin_name)

    scraper = ScraperService()
    result = await scraper.extract_top_ten(origin=origin)

    if result is None:
        return {
            "date": date.today().isoformat(),
            "movies": [],
            "series": [],
        }

    return {
        "date": date.today().isoformat(),
        "movies_count": len(result.movies.items),
        "series_count": len(result.series.items),
    }


async def handle_scrape_popular(job: Job) -> dict:
    origin_name = job.payload.get("origin", "justwatch")
    url = job.payload.get("url")

    if not url:
        raise ValueError("url is required in payload")

    origin = get_site_origin(origin_name)

    max_items = job.payload.get("max_items")
    download_tile_images = job.payload.get("download_tile_images", False)
    download_cast_images = job.payload.get("download_cast_images", False)
    download_background_images = job.payload.get("download_background_images", False)

    scraper = ScraperService()
    result = await scraper.extract_with_origin_detailed(
        url=url,
        origin=origin,
        max_items=max_items,
        download_tile_images=download_tile_images,
        download_cast_images=download_cast_images,
        download_background_images=download_background_images,
    )

    return {
        "url": url,
        "shows_count": len(result.items),
    }
