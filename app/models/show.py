from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import ShowType

if TYPE_CHECKING:
    from .genre import Genre
    from .streaming_option import StreamingOption

show_genres = Table(
    "show_genres",
    Base.metadata,
    Column("show_id", String, ForeignKey("shows.id"), primary_key=True),
    Column("genre_id", String, ForeignKey("genres.id"), primary_key=True),
)


class Show(Base):
    __tablename__ = "shows"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    show_type: Mapped[ShowType] = mapped_column(Enum(ShowType), nullable=False)
    imdb_id: Mapped[str | None] = mapped_column(String, nullable=True)
    tmdb_id: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    original_title: Mapped[str | None] = mapped_column(String, nullable=True)
    overview: Mapped[str | None] = mapped_column(String, nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    first_air_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_air_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    season_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    episode_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    runtime: Mapped[int | None] = mapped_column(Integer, nullable=True)
    directors: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    creators: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    cast: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    image_set: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    genres: Mapped[list["Genre"]] = relationship(secondary=show_genres)
    seasons: Mapped[list["Season"]] = relationship(back_populates="show")
    streaming_options: Mapped[list["StreamingOption"]] = relationship(back_populates="show")


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    show_id: Mapped[str] = mapped_column(String, ForeignKey("shows.id"), nullable=False)
    season_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    first_air_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_air_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    streaming_options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    show: Mapped["Show"] = relationship(back_populates="seasons")
    episodes: Mapped[list["Episode"]] = relationship(back_populates="season")


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasons.id"), nullable=False)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    overview: Mapped[str | None] = mapped_column(String, nullable=True)
    air_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    streaming_options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    season: Mapped["Season"] = relationship(back_populates="episodes")
