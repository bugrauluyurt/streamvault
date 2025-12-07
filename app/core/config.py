from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "streamvault"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen3:30b"

    queue_workers: int = 2
    queue_poll_interval: float = 1.0

    tmdb_api_key: str = ""

    shared_dir: Path = Path("/app/data/shared")

    @property
    def image_tile_dir(self) -> Path:
        return self.shared_dir / "image-tile"

    @property
    def image_background_dir(self) -> Path:
        return self.shared_dir / "image-background"

    @property
    def image_cast_dir(self) -> Path:
        return self.shared_dir / "image-cast"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
