from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from playwright.async_api import Page


class SiteOrigin(ABC):
    @abstractmethod
    def build_url(self, params: dict) -> str:
        pass

    @abstractmethod
    def get_extraction_prompt(self) -> str:
        pass

    @abstractmethod
    def get_extraction_schema(self) -> type[BaseModel]:
        pass

    def get_wait_selector(self) -> str | None:
        return None

    async def extract_from_page(self, page: "Page") -> BaseModel | None:
        return None
