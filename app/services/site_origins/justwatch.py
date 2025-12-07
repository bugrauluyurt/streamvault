import json
import logging
import re
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from pydantic import BaseModel

from app.schemas.enums import ShowType
from app.schemas.scrape import (
    ScrapeCastMember,
    ScrapeGenre,
    ScrapeShow,
    ScrapeShowList,
    ScrapeStreamingOption,
)

from .base import SiteOrigin

if TYPE_CHECKING:
    from playwright.async_api import Page

logger = logging.getLogger(__name__)


class SiteOriginJustWatch(SiteOrigin):
    BASE_URL = "https://www.justwatch.com/us"
    SOURCE_NAME = "justwatch"

    @property
    def name(self) -> str:
        return self.SOURCE_NAME

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

    def get_detail_wait_selector(self) -> str | None:
        return "script[type='application/ld+json']"

    async def extract_from_page(self, page: "Page") -> ScrapeShowList:
        shows: list[ScrapeShow] = []

        links = await page.query_selector_all("a[href*='/us/movie/'], a[href*='/us/tv-show/']")

        for link in links:
            href = await link.get_attribute("href")
            if not href:
                continue

            is_movie = "/us/movie/" in href
            show_type = ShowType.MOVIE if is_movie else ShowType.SERIES

            slug = href.rstrip("/").split("/")[-1]
            title = self._slug_to_title(slug)

            detail_url = f"https://www.justwatch.com{href}" if href.startswith("/") else href

            img = await link.query_selector("img")
            image_url = await img.get_attribute("src") if img else None

            shows.append(
                ScrapeShow(
                    show_type=show_type,
                    source=self.SOURCE_NAME,
                    slug=slug,
                    detail_url=detail_url,
                    title=title,
                    image_url=image_url,
                )
            )

        return ScrapeShowList(items=shows)

    async def extract_detail_page(self, page: "Page", base_show: ScrapeShow) -> ScrapeShow | None:
        json_ld_scripts = await page.query_selector_all("script[type='application/ld+json']")
        if not json_ld_scripts:
            logger.warning("No JSON-LD scripts found for %s", base_show.slug)
            return None

        data: dict[str, Any] | None = None
        for script in json_ld_scripts:
            try:
                json_text = await script.inner_text()
                parsed = json.loads(json_text)
                if parsed.get("@type") in ("Movie", "TVSeries"):
                    data = parsed
                    break
            except (json.JSONDecodeError, Exception) as e:
                logger.debug("Failed to parse JSON-LD script: %s", e)
                continue

        if data is None:
            logger.warning("No Movie/TVSeries JSON-LD found for %s", base_show.slug)
            return None

        logger.debug("Found JSON-LD data for %s: type=%s", base_show.slug, data.get("@type"))

        show_type = self._parse_show_type(data.get("@type"))
        if show_type is None:
            show_type = base_show.show_type

        genres = self._parse_genres(data.get("genre", []))
        directors = self._parse_directors(data.get("director", []))
        creators = self._parse_directors(data.get("author", []))
        cast = await self._extract_cast_with_images(page, data.get("actor", []))
        streaming_options = self._parse_streaming_options(data.get("potentialAction", []))

        aggregate_rating = data.get("aggregateRating", {})
        justwatch_rating = self._parse_int(aggregate_rating.get("ratingValue"))
        rating_count = self._parse_int(aggregate_rating.get("ratingCount"))

        release_year = None
        first_air_year = None
        if show_type == ShowType.MOVIE:
            release_year = self._parse_year(data.get("dateCreated"))
        else:
            first_air_year = self._parse_year(data.get("dateCreated"))
            if not first_air_year:
                first_air_year = self._parse_year(data.get("datePublished"))

        wikidata_id = self._parse_wikidata_id(data.get("sameAs"))

        episode_count = self._parse_int(data.get("numberOfEpisodes"))
        if not episode_count:
            episode_count = self._parse_episode_count_from_seasons(data.get("containsSeason", []))

        return ScrapeShow(
            item_type=base_show.item_type,
            show_type=show_type,
            source=self.SOURCE_NAME,
            slug=base_show.slug,
            detail_url=base_show.detail_url,
            wikidata_id=wikidata_id,
            title=data.get("name", base_show.title),
            overview=data.get("description"),
            release_year=release_year,
            first_air_year=first_air_year,
            genres=genres if genres else None,
            directors=directors if directors else None,
            creators=creators if creators else None,
            cast=cast if cast else None,
            rating=justwatch_rating,
            justwatch_rating=justwatch_rating,
            rating_count=rating_count,
            content_rating=data.get("contentRating"),
            country_of_origin=data.get("countryOfOrigin"),
            season_count=self._parse_int(data.get("numberOfSeasons")),
            episode_count=episode_count,
            runtime=self._parse_duration(data.get("duration")),
            image_url=data.get("image", base_show.image_url),
            local_image_path=base_show.local_image_path,
            streaming_options=streaming_options if streaming_options else None,
        )

    def _slug_to_title(self, slug: str) -> str:
        slug = re.sub(r"-\d+$", "", slug)
        return slug.replace("-", " ").title()

    def _parse_show_type(self, type_str: str | None) -> ShowType | None:
        if not type_str:
            return None
        if type_str == "Movie":
            return ShowType.MOVIE
        if type_str == "TVSeries":
            return ShowType.SERIES
        return None

    def _parse_genres(self, genres: list[str]) -> list[ScrapeGenre]:
        return [ScrapeGenre(id=g.lower().replace(" ", "-"), name=g) for g in genres]

    def _parse_directors(self, people: list[dict[str, Any]]) -> list[str]:
        result: list[str] = []
        for p in people:
            name = p.get("name")
            if name:
                result.append(name)
        return result

    async def _extract_cast_with_images(
        self, page: "Page", actors: list[dict[str, Any]]
    ) -> list[ScrapeCastMember]:
        actor_names: list[str] = []
        for entry in actors:
            if entry.get("@type") == "PerformanceRole":
                actor_obj = entry.get("actor", {})
                name = actor_obj.get("name")
            else:
                name = entry.get("name")
            if name:
                actor_names.append(name)

        cast_elements = await page.query_selector_all(".title-credits__actor")

        cast_with_images: dict[str, str] = {}
        for element in cast_elements:
            img = await element.query_selector("img")
            name_el = await element.query_selector(".title-credit-name")
            if img and name_el:
                name = await name_el.inner_text()
                image_url = await img.get_attribute("src")
                if name and image_url and "images.justwatch.com/portrait" in image_url:
                    cast_with_images[name.strip()] = image_url

        result: list[ScrapeCastMember] = []
        for name in actor_names:
            image_url = cast_with_images.get(name)
            result.append(ScrapeCastMember(name=name, image_url=image_url))

        return result

    def _parse_streaming_options(
        self, actions: list[dict[str, Any]]
    ) -> list[ScrapeStreamingOption]:
        options: list[ScrapeStreamingOption] = []
        for action in actions:
            if action.get("@type") != "WatchAction":
                continue
            target = action.get("target")
            link = target.get("urlTemplate") if isinstance(target, dict) else target
            options.append(
                ScrapeStreamingOption(
                    service_name=action.get("name", "Unknown"),
                    price=action.get("price"),
                    price_currency=action.get("priceCurrency"),
                    link=link,
                )
            )
        return options

    def _parse_int(self, value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _parse_episode_count_from_seasons(self, seasons: list[dict[str, Any]]) -> int | None:
        if not seasons:
            return None
        total = 0
        for season in seasons:
            ep_count = self._parse_int(season.get("numberOfEpisodes"))
            if ep_count:
                total += ep_count
        return total if total > 0 else None

    def _parse_year(self, date_str: str | None) -> int | None:
        if not date_str:
            return None
        match = re.match(r"(\d{4})", date_str)
        return int(match.group(1)) if match else None

    def _parse_duration(self, duration: str | None) -> int | None:
        if not duration:
            return None
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
        if not match:
            return None
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return hours * 60 + minutes if hours or minutes else None

    def _parse_wikidata_id(self, same_as: str | None) -> str | None:
        if not same_as:
            return None
        match = re.search(r"wikidata\.org/wiki/(Q\d+)", same_as)
        return match.group(1) if match else None
