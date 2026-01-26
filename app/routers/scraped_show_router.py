from datetime import date

from fastapi import APIRouter

from app.schemas.scrape import (
    ScrapePopularRequest,
    ScrapeResponse,
    ScrapeTopTenRequest,
    ScrapeTopTenResponse,
)
from app.services.scraper_service import ScraperService
from app.services.site_origins import get_site_origin

router = APIRouter(prefix="/scraped", tags=["scrape"])


@router.post("/popular", response_model=ScrapeResponse)
async def scrape_popular(request: ScrapePopularRequest) -> ScrapeResponse:
    origin = get_site_origin(request.origin)

    scraper = ScraperService()
    result = await scraper.extract_with_origin_detailed(
        url=request.url,
        origin=origin,
        max_items=request.max_items,
        download_tile_images=request.download_tile_images,
        download_cast_images=request.download_cast_images,
        download_background_images=request.download_background_images,
    )

    return ScrapeResponse(shows=result.items, url=request.url)


@router.post("/top-ten", response_model=ScrapeTopTenResponse)
async def scrape_top_ten(request: ScrapeTopTenRequest) -> ScrapeTopTenResponse:
    origin = get_site_origin(request.origin)

    scraper = ScraperService()
    result = await scraper.extract_top_ten(origin=origin)

    if result is None:
        return ScrapeTopTenResponse(
            date=date.today().isoformat(),
            movies=[],
            series=[],
        )

    return ScrapeTopTenResponse(
        date=date.today().isoformat(),
        movies=result.movies.items,
        series=result.series.items,
    )
