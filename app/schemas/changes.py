from pydantic import BaseModel, ConfigDict

from .common import Addon, Service
from .enums import ChangeType, ItemType, ShowType, StreamingOptionType


class Change(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    change_type: ChangeType
    item_type: ItemType
    show_id: str
    show_type: ShowType
    season: int | None = None
    episode: int | None = None
    service: Service
    streaming_option_type: StreamingOptionType
    addon: Addon | None = None
    timestamp: int | None = None
    link: str | None = None
