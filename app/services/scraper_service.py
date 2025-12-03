import contextlib
from typing import TypeVar

from playwright.async_api import async_playwright
from pydantic import BaseModel

from app.services.llm_service import LLMService
from app.services.site_origins.base import SiteOrigin

T = TypeVar("T", bound=BaseModel)


class ScraperService:
    def __init__(self, llm_service: LLMService | None = None):
        self.llm = llm_service or LLMService()

    async def _create_page(self) -> tuple:
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = await context.new_page()
        return p, browser, context, page

    async def _cleanup(self, p, browser, context) -> None:
        await context.close()
        await browser.close()
        await p.stop()

    async def scrape_page(self, url: str, wait_selector: str | None = None) -> str:
        p, browser, context, page = await self._create_page()
        try:
            await page.goto(url, wait_until="networkidle")

            if wait_selector:
                with contextlib.suppress(Exception):
                    await page.wait_for_selector(wait_selector, timeout=10000)

            return await page.content()
        finally:
            await self._cleanup(p, browser, context)

    async def extract_with_origin(self, url: str, origin: SiteOrigin) -> BaseModel:
        p, browser, context, page = await self._create_page()
        try:
            await page.goto(url, wait_until="networkidle")

            wait_selector = origin.get_wait_selector()
            if wait_selector:
                with contextlib.suppress(Exception):
                    await page.wait_for_selector(wait_selector, timeout=10000)

            result = await origin.extract_from_page(page)
            if result is not None:
                return result

            content = await page.content()
            return await self.llm.extract_structured(
                content, origin.get_extraction_schema(), origin.get_extraction_prompt()
            )
        finally:
            await self._cleanup(p, browser, context)

    async def extract_data(
        self,
        url: str,
        schema: type[T],
        prompt: str | None = None,
        wait_selector: str | None = None,
    ) -> T:
        html = await self.scrape_page(url, wait_selector)
        return await self.llm.extract_structured(html, schema, prompt)

    async def scrape_and_generate(self, url: str, prompt: str) -> str:
        html = await self.scrape_page(url)
        full_prompt = f"{prompt}\n\nContent:\n{html}"
        return await self.llm.generate(full_prompt)
