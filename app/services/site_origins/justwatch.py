import re
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from pydantic import BaseModel

from app.schemas.enums import ShowType
from app.schemas.scrape import ScrapeShow, ScrapeShowList

from .base import SiteOrigin

if TYPE_CHECKING:
    from playwright.async_api import Page


class SiteOriginJustWatch(SiteOrigin):
    BASE_URL = "https://www.justwatch.com/us"

    def build_url(self, params: dict[str, Any]) -> str:
        query_params: dict[str, str] = {}

        if providers := params.get("providers"):
            query_params["providers"] = ",".join(providers)

        if rating_imdb := params.get("rating_imdb"):
            if isinstance(rating_imdb, list) and len(rating_imdb) >= 2:
                query_params["rating_imdb"] = f"{rating_imdb[0]}.{rating_imdb[1]}"
            elif isinstance(rating_imdb, list) and len(rating_imdb) == 1:
                query_params["rating_imdb"] = str(rating_imdb[0])

        if tomato_meter := params.get("tomato_meter"):
            query_params["tomatoMeter"] = str(tomato_meter)

        if not query_params:
            return self.BASE_URL

        return f"{self.BASE_URL}?{urlencode(query_params)}"

    def get_extraction_prompt(self) -> str:
        return """Extract all movie and TV show listings from this JustWatch page.
For each show, extract:
- item_type: Always "show"
- show_type: Either "movie" or "series"
- imdb_id: The IMDB ID if available (format: tt1234567)
- tmdb_id: The TMDB ID if available
- title: The name of the movie or TV show
- overview: Brief description/synopsis if available
- release_year: The release year for movies
- first_air_year: First air year for series
- last_air_year: Last air year for series (if ended)
- original_title: Original title if different from title
- genres: List of genres with id and name (e.g., [{"id": "action", "name": "Action"}])
- directors: List of director names
- creators: List of creator names (for series)
- cast: List of main cast member names
- rating: The rating as an integer (0-100 scale)
- season_count: Number of seasons (for series)
- episode_count: Total episode count (for series)
- runtime: Runtime in minutes
- image_url: The poster image URL if available
- streaming_services: List of streaming service names where it's available

Return all shows found on the page."""

    def get_extraction_schema(self) -> type[BaseModel]:
        return ScrapeShowList

    def get_wait_selector(self) -> str | None:
        return "a[href*='/us/movie/'], a[href*='/us/tv-show/']"

    async def extract_from_page(self, page: "Page") -> ScrapeShowList:
        shows: list[ScrapeShow] = []

        links = await page.query_selector_all("a[href*='/us/movie/'], a[href*='/us/tv-show/']")

        for link in links:
            href = await link.get_attribute("href")
            if not href:
                continue

            is_movie = "/us/movie/" in href
            show_type = ShowType.MOVIE if is_movie else ShowType.SERIES

            slug = href.split("/")[-1]
            title = self._slug_to_title(slug)

            img = await link.query_selector("img")
            image_url = await img.get_attribute("src") if img else None

            shows.append(
                ScrapeShow(
                    show_type=show_type,
                    title=title,
                    image_url=image_url,
                )
            )

        return ScrapeShowList(items=shows)

    def _slug_to_title(self, slug: str) -> str:
        slug = re.sub(r"-\d+$", "", slug)
        return slug.replace("-", " ").title()
