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


class ScrapeGenre(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str


class ScrapeShow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item_type: ItemType = ItemType.SHOW
    show_type: ShowType
    imdb_id: str | None = None
    tmdb_id: str | None = None
    title: str
    overview: str | None = None
    release_year: int | None = None
    first_air_year: int | None = None
    last_air_year: int | None = None
    original_title: str | None = None
    genres: list[ScrapeGenre] | None = None
    directors: list[str] | None = None
    creators: list[str] | None = None
    cast: list[str] | None = None
    rating: int | None = None
    season_count: int | None = None
    episode_count: int | None = None
    runtime: int | None = None
    image_url: str | None = None
    streaming_services: list[str] | None = None


class ScrapeShowList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ScrapeShow]


class ScrapeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    shows: list[ScrapeShow]
    url: str
