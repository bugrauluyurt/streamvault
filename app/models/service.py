from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .country import Country


class Addon(Base):
    __tablename__ = "addons"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    home_page: Mapped[str] = mapped_column(String, nullable=False)
    theme_color_code: Mapped[str] = mapped_column(String, nullable=False)
    image_set: Mapped[dict] = mapped_column(JSONB, nullable=False)
    service_id: Mapped[str | None] = mapped_column(String, ForeignKey("services.id"), nullable=True)

    service: Mapped["Service | None"] = relationship(back_populates="addons")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    home_page: Mapped[str] = mapped_column(String, nullable=False)
    theme_color_code: Mapped[str] = mapped_column(String, nullable=False)
    image_set: Mapped[dict] = mapped_column(JSONB, nullable=False)
    streaming_option_types: Mapped[dict] = mapped_column(JSONB, nullable=False)

    addons: Mapped[list["Addon"]] = relationship(back_populates="service")
    countries: Mapped[list["Country"]] = relationship(
        secondary="country_services", back_populates="services"
    )
