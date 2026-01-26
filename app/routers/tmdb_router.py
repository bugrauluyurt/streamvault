from fastapi import APIRouter

from app.schemas.tmdb import (
    TMDBMovieDetails,
    TMDBMovieSearchResult,
    TMDBSearchResponse,
    TMDBTVDetails,
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


@router.get("/movies/{movie_id}", response_model=TMDBMovieDetails)
async def get_movie_details(movie_id: int) -> TMDBMovieDetails:
    service = TMDBService()
    try:
        return await service.get_movie_details(movie_id)
    finally:
        await service.close()


@router.get("/tv/{tv_id}", response_model=TMDBTVDetails)
async def get_tv_details(tv_id: int) -> TMDBTVDetails:
    service = TMDBService()
    try:
        return await service.get_tv_details(tv_id)
    finally:
        await service.close()


@router.get("/tv/{tv_id}/season/{season_number}")
async def get_tv_season(tv_id: int, season_number: int) -> dict:
    """Get season details including all episodes."""
    service = TMDBService()
    try:
        return await service.get_tv_season(tv_id, season_number)
    finally:
        await service.close()
