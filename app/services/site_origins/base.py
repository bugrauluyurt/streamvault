from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from playwright.async_api import Page

from app.schemas.scrape import ScrapeShow, ScrapeShowList


class TopTenResult:
    def __init__(self, movies: ScrapeShowList, series: ScrapeShowList):
        self.movies = movies
        self.series = series


class SiteOrigin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def build_url(self, params: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def get_extraction_prompt(self) -> str:
        pass

    @abstractmethod
    def get_extraction_schema(self) -> type[BaseModel]:
        pass

    def get_wait_selector(self) -> str | None:
        return None

    def get_detail_wait_selector(self) -> str | None:
        return None

    async def extract_from_page(self, page: "Page") -> BaseModel | None:
        return None

    async def extract_detail_page(self, page: "Page", base_show: ScrapeShow) -> ScrapeShow | None:
        return None

    def get_top_ten_url(self) -> str | None:
        return None

    def get_top_ten_wait_selector(self) -> str | None:
        return None

    async def extract_top_ten(self, page: "Page") -> TopTenResult | None:
        return None
