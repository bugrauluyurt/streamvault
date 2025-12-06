from fastapi import APIRouter

from app.schemas.scrape import ScrapeRequest, ScrapeResponse
from app.services.scraper_service import ScraperService
from app.services.site_origins import get_site_origin

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("", response_model=ScrapeResponse)
async def scrape_shows(request: ScrapeRequest) -> ScrapeResponse:
    origin = get_site_origin(request.site_params.origin)
    url = origin.build_url(request.site_params.params.model_dump())

    scraper = ScraperService()
    result = await scraper.extract_with_origin_detailed(url=url, origin=origin)

    return ScrapeResponse(shows=result.items, url=url)
