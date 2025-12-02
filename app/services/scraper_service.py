from typing import TypeVar

from playwright.async_api import async_playwright
from pydantic import BaseModel

from app.services.llm_service import LLMService

T = TypeVar("T", bound=BaseModel)


class ScraperService:
    def __init__(self, llm_service: LLMService | None = None):
        self.llm = llm_service or LLMService()

    async def scrape_page(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            await browser.close()
            return content

    async def extract_data(
        self,
        url: str,
        schema: type[T],
        prompt: str | None = None,
    ) -> T:
        html = await self.scrape_page(url)
        return await self.llm.extract_structured(html, schema, prompt)

    async def scrape_and_generate(self, url: str, prompt: str) -> str:
        html = await self.scrape_page(url)
        full_prompt = f"{prompt}\n\nContent:\n{html}"
        return await self.llm.generate(full_prompt)
