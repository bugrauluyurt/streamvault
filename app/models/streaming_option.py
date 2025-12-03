from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import Quality, StreamingOptionType

if TYPE_CHECKING:
    from .service import Addon, Service
    from .show import Show


class StreamingOption(Base):
    __tablename__ = "streaming_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    show_id: Mapped[str] = mapped_column(String, ForeignKey("shows.id"), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    service_id: Mapped[str] = mapped_column(String, ForeignKey("services.id"), nullable=False)
    type: Mapped[StreamingOptionType] = mapped_column(Enum(StreamingOptionType), nullable=False)
    link: Mapped[str] = mapped_column(String, nullable=False)
    video_link: Mapped[str | None] = mapped_column(String, nullable=True)
    quality: Mapped[Quality | None] = mapped_column(Enum(Quality), nullable=True)
    audios: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    subtitles: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    price: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    addon_id: Mapped[str | None] = mapped_column(String, ForeignKey("addons.id"), nullable=True)
    expires_soon: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    available_since: Mapped[int | None] = mapped_column(Integer, nullable=True)

    show: Mapped["Show"] = relationship(back_populates="streaming_options")
    service: Mapped["Service"] = relationship()
    addon: Mapped["Addon | None"] = relationship()
