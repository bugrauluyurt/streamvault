from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums import ScrapedType, ShowType


class ScrapedShowResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    tmdb_id: str | None
    name: str
    details: dict
    type: ScrapedType
    source_url: str
    created_at: datetime
    updated_at: datetime


class ScrapedShowListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ScrapedShowResponse]
    total: int
    skip: int
    limit: int


class TopTenShowItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    position: int
    show_type: ShowType
    show: ScrapedShowResponse


class TopTenShowsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    movies: list[TopTenShowItem]
    series: list[TopTenShowItem]
