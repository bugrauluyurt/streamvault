from fastapi import APIRouter

from app.schemas.tmdb import (
    TMDBMovieSearchResult,
    TMDBSearchResponse,
    TMDBTVSearchResult,
)
from app.services.tmdb_service import TMDBService

router = APIRouter(prefix="/tmdb", tags=["tmdb"])


@router.get("/search/movies", response_model=TMDBSearchResponse[TMDBMovieSearchResult])
async def search_movies(
    query: str,
    page: int = 1,
    include_details: bool = False,
) -> TMDBSearchResponse[TMDBMovieSearchResult]:
    service = TMDBService()
    try:
        return await service.search_movies(query=query, page=page, include_details=include_details)
    finally:
        await service.close()


@router.get("/search/tv", response_model=TMDBSearchResponse[TMDBTVSearchResult])
async def search_tv(
    query: str,
    page: int = 1,
    include_details: bool = False,
) -> TMDBSearchResponse[TMDBTVSearchResult]:
    service = TMDBService()
    try:
        return await service.search_tv(query=query, page=page, include_details=include_details)
    finally:
        await service.close()
