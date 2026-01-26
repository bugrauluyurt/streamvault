from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.enums import ShowType
from app.helpers.tmdb_enrichment import enrich_popular_with_tmdb, enrich_topten_with_tmdb
from app.schemas.shows import (
    PopularShowItem,
    PopularShowsResponse,
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
    enrich_tmdb: bool = False,
    db: AsyncSession = Depends(get_db),
) -> TopTenShowsResponse:
    service = ShowsService(db)
    movies, series = await service.get_top_ten_shows()

    movie_items = [TopTenShowItem.model_validate(movie) for movie in movies]
    series_items = [TopTenShowItem.model_validate(s) for s in series]

    if enrich_tmdb:
        movie_items = await enrich_topten_with_tmdb(movie_items, "movie")
        series_items = await enrich_topten_with_tmdb(series_items, "tv")

    return TopTenShowsResponse(movies=movie_items, series=series_items)


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


@router.get("/popular/movies", response_model=PopularShowsResponse)
async def get_popular_movies(
    limit: int = 20,
    enrich_tmdb: bool = False,
    db: AsyncSession = Depends(get_db),
) -> PopularShowsResponse:
    service = ShowsService(db)
    shows = await service.get_popular_shows(ShowType.MOVIE, limit=limit)
    items = [PopularShowItem.model_validate(show) for show in shows]

    if enrich_tmdb:
        items = await enrich_popular_with_tmdb(items, "movie")

    return PopularShowsResponse(items=items)


@router.get("/popular/series", response_model=PopularShowsResponse)
async def get_popular_series(
    limit: int = 20,
    enrich_tmdb: bool = False,
    db: AsyncSession = Depends(get_db),
) -> PopularShowsResponse:
    service = ShowsService(db)
    shows = await service.get_popular_shows(ShowType.SERIES, limit=limit)
    items = [PopularShowItem.model_validate(show) for show in shows]

    if enrich_tmdb:
        items = await enrich_popular_with_tmdb(items, "tv")

    return PopularShowsResponse(items=items)
