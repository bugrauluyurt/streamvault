from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .service import Service

country_services = Table(
    "country_services",
    Base.metadata,
    Column("country_code", String, ForeignKey("countries.country_code"), primary_key=True),
    Column("service_id", String, ForeignKey("services.id"), primary_key=True),
)


class Country(Base):
    __tablename__ = "countries"

    country_code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    services: Mapped[list["Service"]] = relationship(
        secondary=country_services, back_populates="countries"
    )
