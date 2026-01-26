import asyncio

from app.schemas.shows import PopularShowItem, TopTenShowItem
from app.services.tmdb_cache import get_tmdb_images
from app.services.tmdb_service import TMDBService


async def enrich_popular_with_tmdb(
    items: list[PopularShowItem], media_type: str
) -> list[PopularShowItem]:
    await _do_enrich(items, media_type)
    return items


async def enrich_topten_with_tmdb(
    items: list[TopTenShowItem], media_type: str
) -> list[TopTenShowItem]:
    await _do_enrich(items, media_type)
    return items


async def _do_enrich(items: list[PopularShowItem] | list[TopTenShowItem], media_type: str) -> None:
    tmdb = TMDBService()
    try:
        tasks = []
        for item in items:
            if item.tmdb_id:
                tmdb_id = int(item.tmdb_id)
                tasks.append(get_tmdb_images(tmdb, media_type, tmdb_id))
            else:

                async def empty_result() -> dict[str, str | None]:
                    return {"backdrop_path": None, "poster_path": None}

                tasks.append(empty_result())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception) or not isinstance(result, dict):
                continue
            if items[i].details is None:
                continue
            items[i].details["tmdb_backdrop_path"] = result.get("backdrop_path")
            items[i].details["tmdb_poster_path"] = result.get("poster_path")
    finally:
        await tmdb.close()
