from pydantic import BaseModel, ConfigDict, Field


class TMDBGenre(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str


class TMDBProductionCompany(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    logo_path: str | None = None
    origin_country: str | None = None


class TMDBCastMember(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    character: str | None = None
    profile_path: str | None = None
    order: int | None = None


class TMDBCrewMember(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    job: str
    department: str
    profile_path: str | None = None


class TMDBCredits(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cast: list[TMDBCastMember] = Field(default_factory=list)
    crew: list[TMDBCrewMember] = Field(default_factory=list)


class TMDBMovieSearchResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    original_title: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    release_date: str | None = None
    genre_ids: list[int] = Field(default_factory=list)
    popularity: float | None = None
    vote_average: float | None = None
    vote_count: int | None = None
    adult: bool = False
    original_language: str | None = None


class TMDBTVSearchResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    original_name: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    first_air_date: str | None = None
    genre_ids: list[int] = Field(default_factory=list)
    popularity: float | None = None
    vote_average: float | None = None
    vote_count: int | None = None
    origin_country: list[str] = Field(default_factory=list)
    original_language: str | None = None


class TMDBMovieDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    original_title: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    release_date: str | None = None
    genres: list[TMDBGenre] = Field(default_factory=list)
    popularity: float | None = None
    vote_average: float | None = None
    vote_count: int | None = None
    adult: bool = False
    original_language: str | None = None
    runtime: int | None = None
    budget: int | None = None
    revenue: int | None = None
    status: str | None = None
    tagline: str | None = None
    homepage: str | None = None
    imdb_id: str | None = None
    production_companies: list[TMDBProductionCompany] = Field(default_factory=list)
    credits: TMDBCredits | None = None


class TMDBTVDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    original_name: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    first_air_date: str | None = None
    last_air_date: str | None = None
    genres: list[TMDBGenre] = Field(default_factory=list)
    popularity: float | None = None
    vote_average: float | None = None
    vote_count: int | None = None
    origin_country: list[str] = Field(default_factory=list)
    original_language: str | None = None
    number_of_seasons: int | None = None
    number_of_episodes: int | None = None
    episode_run_time: list[int] = Field(default_factory=list)
    status: str | None = None
    tagline: str | None = None
    homepage: str | None = None
    in_production: bool | None = None
    production_companies: list[TMDBProductionCompany] = Field(default_factory=list)
    credits: TMDBCredits | None = None


class TMDBSearchResponse[T](BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    page: int
    total_pages: int
    total_results: int
    results: list[T]
