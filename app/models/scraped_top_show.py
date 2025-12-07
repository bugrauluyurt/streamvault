from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import ShowType

from .base import Base
from .scraped import ScrapedShow


class ScrapedTopShow(Base):
    __tablename__ = "scraped_top_shows"

    id: Mapped[int] = mapped_column(primary_key=True)
    show_id: Mapped[int] = mapped_column(ForeignKey("scraped_shows.id"), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    show_type: Mapped[ShowType] = mapped_column(String, nullable=False)
    batch_sequence: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    show: Mapped[ScrapedShow] = relationship("ScrapedShow")

    __table_args__ = (Index("ix_scraped_top_shows_batch_sequence", "batch_sequence"),)
