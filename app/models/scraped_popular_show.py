from datetime import datetime

from sqlalchemy import Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import ShowType, ValidationStatus

from .base import Base


class ScrapedPopularShow(Base):
    __tablename__ = "scraped_popular_shows"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[str | None] = mapped_column(String, nullable=True)
    position: Mapped[int] = mapped_column(nullable=False)
    show_type: Mapped[ShowType] = mapped_column(String, nullable=False)
    batch_sequence: Mapped[int] = mapped_column(nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False)
    validation_status: Mapped[ValidationStatus] = mapped_column(
        String, nullable=False, server_default=ValidationStatus.NOT_STARTED.value
    )
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    __table_args__ = (Index("ix_scraped_popular_shows_batch_sequence", "batch_sequence"),)
