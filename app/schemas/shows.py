from pydantic import BaseModel, ConfigDict

from .common import Addon, Genre, ImageSet, Locale, Price, Service, Subtitle
from .enums import ItemType, Quality, ShowType, StreamingOptionType


class StreamingOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    service: Service
    type: StreamingOptionType
    link: str
    video_link: str | None = None
    quality: Quality | None = None
    audios: list[Locale] | None = None
    subtitles: list[Subtitle] | None = None
    price: Price | None = None
    addon: Addon | None = None
    expires_soon: bool = False
    available_since: int | None = None


class Episode(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item_type: ItemType = ItemType.EPISODE
    title: str
    overview: str | None = None
    air_year: int | None = None
    streaming_options: dict[str, list[StreamingOption]] | None = None


class Season(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item_type: ItemType = ItemType.SEASON
    title: str
    first_air_year: int | None = None
    last_air_year: int | None = None
    streaming_options: dict[str, list[StreamingOption]] | None = None
    episodes: list[Episode] | None = None


class Show(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item_type: ItemType = ItemType.SHOW
    show_type: ShowType
    id: str
    imdb_id: str | None = None
    tmdb_id: str | None = None
    title: str
    overview: str | None = None
    release_year: int | None = None
    first_air_year: int | None = None
    last_air_year: int | None = None
    original_title: str | None = None
    genres: list[Genre] | None = None
    directors: list[str] | None = None
    creators: list[str] | None = None
    cast: list[str] | None = None
    rating: int | None = None
    season_count: int | None = None
    episode_count: int | None = None
    runtime: int | None = None
    image_set: ImageSet | None = None
    streaming_options: dict[str, list[StreamingOption]] | None = None
    seasons: list[Season] | None = None
