from pydantic import BaseModel, ConfigDict

from .common import Service


class Country(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    country_code: str
    name: str
    services: list[Service] | None = None
