from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.shows import (
    ScrapedShowListResponse,
    ScrapedShowResponse,
    TopTenShowItem,
    TopTenShowsResponse,
)
from app.services.shows_service import ShowsService

router = APIRouter(prefix="/shows", tags=["shows"])


@router.get("/scraped", response_model=ScrapedShowListResponse)
async def get_scraped_shows(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ScrapedShowListResponse:
    service = ShowsService(db)
    shows, total = await service.get_scraped_shows(skip=skip, limit=limit)

    return ScrapedShowListResponse(
        items=[ScrapedShowResponse.model_validate(show) for show in shows],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/scraped/top-ten", response_model=TopTenShowsResponse)
async def get_top_ten_shows(
    db: AsyncSession = Depends(get_db),
) -> TopTenShowsResponse:
    service = ShowsService(db)
    movies, series = await service.get_top_ten_shows()

    return TopTenShowsResponse(
        movies=[TopTenShowItem.model_validate(movie) for movie in movies],
        series=[TopTenShowItem.model_validate(s) for s in series],
    )


@router.get("/scraped/{show_id}", response_model=ScrapedShowResponse)
async def get_scraped_show(
    show_id: int,
    db: AsyncSession = Depends(get_db),
) -> ScrapedShowResponse:
    service = ShowsService(db)
    show = await service.get_scraped_show_by_id(show_id)

    if show is None:
        raise HTTPException(status_code=404, detail="Show not found")

    return ScrapedShowResponse.model_validate(show)
