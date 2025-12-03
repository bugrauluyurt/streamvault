from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import ChangeType, ItemType, ShowType, StreamingOptionType

if TYPE_CHECKING:
    from .service import Addon, Service


class Change(Base):
    __tablename__ = "changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    change_type: Mapped[ChangeType] = mapped_column(Enum(ChangeType), nullable=False)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False)
    show_id: Mapped[str] = mapped_column(String, nullable=False)
    show_type: Mapped[ShowType] = mapped_column(Enum(ShowType), nullable=False)
    season: Mapped[int | None] = mapped_column(Integer, nullable=True)
    episode: Mapped[int | None] = mapped_column(Integer, nullable=True)
    service_id: Mapped[str] = mapped_column(String, ForeignKey("services.id"), nullable=False)
    streaming_option_type: Mapped[StreamingOptionType] = mapped_column(
        Enum(StreamingOptionType), nullable=False
    )
    addon_id: Mapped[str | None] = mapped_column(String, ForeignKey("addons.id"), nullable=True)
    timestamp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    link: Mapped[str | None] = mapped_column(String, nullable=True)

    service: Mapped["Service"] = relationship()
    addon: Mapped["Addon | None"] = relationship()
