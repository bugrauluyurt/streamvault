"""
In-memory TTL cache for TMDB API responses.

Caches backdrop_path and poster_path to avoid repeated TMDB API calls.
Cache is lost on restart but that's fine - data is easily refetchable.
"""

from cachetools import TTLCache

from app.schemas.tmdb import TMDBMovieDetails, TMDBTVDetails
from app.services.tmdb_service import TMDBService

# Cache config
CACHE_TTL = 24 * 60 * 60  # 24 hours in seconds
CACHE_MAX_SIZE = 1000  # Max items to cache

# Global cache instance
_image_cache: TTLCache[str, dict[str, str | None]] = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL)


def _cache_key(media_type: str, tmdb_id: int) -> str:
    """Generate cache key for TMDB image paths."""
    return f"tmdb:{media_type}:{tmdb_id}"


def get_cached_images(media_type: str, tmdb_id: int) -> dict[str, str | None] | None:
    """Get cached image paths if available."""
    key = _cache_key(media_type, tmdb_id)
    return _image_cache.get(key)


def set_cached_images(
    media_type: str, tmdb_id: int, backdrop_path: str | None, poster_path: str | None
) -> None:
    """Cache image paths for a TMDB item."""
    key = _cache_key(media_type, tmdb_id)
    _image_cache[key] = {
        "backdrop_path": backdrop_path,
        "poster_path": poster_path,
    }


async def get_tmdb_images(
    tmdb_service: TMDBService, media_type: str, tmdb_id: int
) -> dict[str, str | None]:
    """
    Get TMDB image paths with caching.

    Checks cache first, fetches from TMDB if not cached, then caches result.
    """
    # Check cache first
    cached = get_cached_images(media_type, tmdb_id)
    if cached is not None:
        return cached

    # Fetch from TMDB
    try:
        if media_type == "movie":
            details: TMDBMovieDetails | TMDBTVDetails = await tmdb_service.get_movie_details(
                tmdb_id
            )
        else:
            details = await tmdb_service.get_tv_details(tmdb_id)

        backdrop_path = details.backdrop_path
        poster_path = details.poster_path

        # Cache the result
        set_cached_images(media_type, tmdb_id, backdrop_path, poster_path)

        return {"backdrop_path": backdrop_path, "poster_path": poster_path}
    except Exception:
        # On error, return empty and don't cache
        return {"backdrop_path": None, "poster_path": None}


def cache_stats() -> dict[str, int]:
    return {
        "size": len(_image_cache),
        "max_size": int(_image_cache.maxsize),
        "ttl": CACHE_TTL,
    }
