from typing import Literal

from pydantic import BaseModel, ConfigDict

from .enums import ItemType, ShowType


class JustWatchParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    providers: list[str]
    rating_imdb: list[int] | None = None
    tomato_meter: int | None = None


class SiteParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    origin: Literal["justwatch"]
    params: JustWatchParams


class ScrapeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    site_params: SiteParams
    max_items: int | None = None


class ScrapeGenre(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str


class ScrapeStreamingOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    service_name: str
    type: str | None = None
    price: str | None = None
    price_currency: str | None = None
    link: str | None = None


class ScrapeCastMember(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    image_url: str | None = None
    local_image_path: str | None = None


class ScrapeShow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item_type: ItemType = ItemType.SHOW
    show_type: ShowType
    source: str | None = None
    slug: str | None = None
    detail_url: str | None = None
    imdb_id: str | None = None
    tmdb_id: str | None = None
    wikidata_id: str | None = None
    title: str
    overview: str | None = None
    release_year: int | None = None
    first_air_year: int | None = None
    last_air_year: int | None = None
    original_title: str | None = None
    genres: list[ScrapeGenre] | None = None
    directors: list[str] | None = None
    creators: list[str] | None = None
    cast: list[ScrapeCastMember] | None = None
    rating: int | None = None
    justwatch_rating: int | None = None
    rating_count: int | None = None
    content_rating: str | None = None
    country_of_origin: str | None = None
    season_count: int | None = None
    episode_count: int | None = None
    runtime: int | None = None
    image_url: str | None = None
    local_image_path: str | None = None
    streaming_services: list[str] | None = None
    streaming_options: list[ScrapeStreamingOption] | None = None


class ScrapeShowList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ScrapeShow]


class ScrapeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    shows: list[ScrapeShow]
    url: str
