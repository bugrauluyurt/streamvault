import asyncio

import httpx

from app.core.config import settings
from app.schemas.tmdb import (
    TMDBMovieDetails,
    TMDBMovieSearchResult,
    TMDBSearchResponse,
    TMDBTVDetails,
    TMDBTVSearchResult,
)


class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.tmdb_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={"Accept": "application/json"},
                timeout=30.0,
            )
        return self._client

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        client = await self._get_client()
        params = kwargs.pop("params", {})
        params["api_key"] = self.api_key
        response = await client.request(method, path, params=params, **kwargs)
        response.raise_for_status()
        return response.json()

    async def search_movies(
        self,
        query: str,
        page: int = 1,
        include_adult: bool = False,
        language: str = "en-US",
        year: int | None = None,
        include_details: bool = False,
    ) -> TMDBSearchResponse[TMDBMovieSearchResult]:
        params: dict[str, str | int | bool] = {
            "query": query,
            "page": page,
            "include_adult": include_adult,
            "language": language,
        }
        if year:
            params["year"] = year

        data = await self._request("GET", "/search/movie", params=params)
        response = TMDBSearchResponse[TMDBMovieSearchResult](
            page=data["page"],
            total_pages=data["total_pages"],
            total_results=data["total_results"],
            results=[TMDBMovieSearchResult.model_validate(r) for r in data["results"]],
        )

        if include_details and response.results:
            details = await asyncio.gather(
                *[self.get_movie_details(r.id) for r in response.results],
                return_exceptions=True,
            )
            detailed_results: list[TMDBMovieSearchResult] = []
            for i, detail in enumerate(details):
                if isinstance(detail, TMDBMovieDetails):
                    detailed_results.append(
                        TMDBMovieSearchResult(
                            id=detail.id,
                            title=detail.title,
                            original_title=detail.original_title,
                            overview=detail.overview,
                            poster_path=detail.poster_path,
                            backdrop_path=detail.backdrop_path,
                            release_date=detail.release_date,
                            genre_ids=[g.id for g in detail.genres],
                            popularity=detail.popularity,
                            vote_average=detail.vote_average,
                            vote_count=detail.vote_count,
                            adult=detail.adult,
                            original_language=detail.original_language,
                        )
                    )
                else:
                    detailed_results.append(response.results[i])
            response.results = detailed_results

        return response

    async def search_tv(
        self,
        query: str,
        page: int = 1,
        include_adult: bool = False,
        language: str = "en-US",
        first_air_date_year: int | None = None,
        include_details: bool = False,
    ) -> TMDBSearchResponse[TMDBTVSearchResult]:
        params: dict[str, str | int | bool] = {
            "query": query,
            "page": page,
            "include_adult": include_adult,
            "language": language,
        }
        if first_air_date_year:
            params["first_air_date_year"] = first_air_date_year

        data = await self._request("GET", "/search/tv", params=params)
        response = TMDBSearchResponse[TMDBTVSearchResult](
            page=data["page"],
            total_pages=data["total_pages"],
            total_results=data["total_results"],
            results=[TMDBTVSearchResult.model_validate(r) for r in data["results"]],
        )

        if include_details and response.results:
            details = await asyncio.gather(
                *[self.get_tv_details(r.id) for r in response.results],
                return_exceptions=True,
            )
            detailed_results: list[TMDBTVSearchResult] = []
            for i, detail in enumerate(details):
                if isinstance(detail, TMDBTVDetails):
                    detailed_results.append(
                        TMDBTVSearchResult(
                            id=detail.id,
                            name=detail.name,
                            original_name=detail.original_name,
                            overview=detail.overview,
                            poster_path=detail.poster_path,
                            backdrop_path=detail.backdrop_path,
                            first_air_date=detail.first_air_date,
                            genre_ids=[g.id for g in detail.genres],
                            popularity=detail.popularity,
                            vote_average=detail.vote_average,
                            vote_count=detail.vote_count,
                            origin_country=detail.origin_country,
                            original_language=detail.original_language,
                        )
                    )
                else:
                    detailed_results.append(response.results[i])
            response.results = detailed_results

        return response

    async def get_movie_details(
        self,
        movie_id: int,
        language: str = "en-US",
        append_to_response: str | None = "credits",
    ) -> TMDBMovieDetails:
        params: dict[str, str] = {"language": language}
        if append_to_response:
            params["append_to_response"] = append_to_response

        data = await self._request("GET", f"/movie/{movie_id}", params=params)
        return TMDBMovieDetails.model_validate(data)

    async def get_tv_details(
        self,
        tv_id: int,
        language: str = "en-US",
        append_to_response: str | None = "credits",
    ) -> TMDBTVDetails:
        params: dict[str, str] = {"language": language}
        if append_to_response:
            params["append_to_response"] = append_to_response

        data = await self._request("GET", f"/tv/{tv_id}", params=params)
        return TMDBTVDetails.model_validate(data)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
