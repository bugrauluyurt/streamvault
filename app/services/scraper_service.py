import asyncio
import contextlib
import logging
from pathlib import Path
from typing import TypeVar

import httpx
from playwright.async_api import BrowserContext, Page, Playwright, async_playwright
from playwright.async_api._generated import Browser
from pydantic import BaseModel

from app.core.config import settings
from app.schemas.scrape import ScrapeCastMember, ScrapeShow, ScrapeShowList
from app.services.llm_service import LLMService
from app.services.site_origins.base import SiteOrigin

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ScraperService:
    def __init__(self, llm_service: LLMService | None = None):
        self.llm = llm_service or LLMService()
        settings.image_tile_dir.mkdir(parents=True, exist_ok=True)
        settings.image_background_dir.mkdir(parents=True, exist_ok=True)
        settings.image_cast_dir.mkdir(parents=True, exist_ok=True)

    def _get_image_extension(self, image_url: str) -> str:
        url_lower = image_url.lower()
        if ".avif" in url_lower:
            return ".avif"
        if ".png" in url_lower:
            return ".png"
        if ".webp" in url_lower:
            return ".webp"
        return ".jpg"

    async def _download_image(
        self, image_url: str, slug: str, source: str, target_dir: Path | None = None
    ) -> str | None:
        if not image_url or image_url.startswith("data:"):
            return None

        ext = self._get_image_extension(image_url)
        filename = f"{source}_{slug}{ext}"
        directory = target_dir if target_dir else settings.image_tile_dir
        filepath = directory / filename

        if filepath.exists():
            return filename

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30.0)
                if response.status_code == 200:
                    filepath.write_bytes(response.content)
                    return filename
        except Exception:
            pass
        return None

    async def _download_cast_image(self, image_url: str, actor_name: str) -> str | None:
        if not image_url or image_url.startswith("data:"):
            return None

        ext = self._get_image_extension(image_url)
        filename = f"{actor_name.lower().replace(' ', '_')}{ext}"
        filepath = settings.image_cast_dir / filename

        if filepath.exists():
            return filename

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30.0)
                if response.status_code == 200:
                    filepath.write_bytes(response.content)
                    return filename
        except Exception:
            pass
        return None

    async def _create_page(self) -> tuple[Playwright, Browser, BrowserContext, Page]:
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=False)
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

    async def _cleanup(self, p: Playwright, browser: Browser, context: BrowserContext) -> None:
        await context.close()
        await browser.close()
        await p.stop()

    async def scrape_page(self, url: str, wait_selector: str | None = None) -> str:
        p, browser, context, page = await self._create_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")

            if wait_selector:
                with contextlib.suppress(Exception):
                    await page.wait_for_selector(wait_selector, timeout=10000)

            return await page.content()
        finally:
            await self._cleanup(p, browser, context)

    async def extract_with_origin(self, url: str, origin: SiteOrigin) -> BaseModel:
        p, browser, context, page = await self._create_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")

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

    async def extract_with_origin_detailed(
        self, url: str, origin: SiteOrigin, max_concurrent: int = 5, max_items: int | None = None
    ) -> ScrapeShowList:
        p, browser, context, page = await self._create_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")

            wait_selector = origin.get_wait_selector()
            if wait_selector:
                with contextlib.suppress(Exception):
                    await page.wait_for_selector(wait_selector, timeout=10000)

            await asyncio.sleep(5)
            await page.evaluate("window.scrollBy(0, 2000)")
            await asyncio.sleep(5)
            logger.debug("Main page loaded, extracting shows from listing")

            result = await origin.extract_from_page(page)

            if result is None or not isinstance(result, ScrapeShowList):
                content = await page.content()
                result = await self.llm.extract_structured(
                    content, origin.get_extraction_schema(), origin.get_extraction_prompt()
                )
                if not isinstance(result, ScrapeShowList):
                    return ScrapeShowList(items=[])

            images_saved = 0

            async def download_show_image(show: ScrapeShow) -> ScrapeShow:
                nonlocal images_saved
                if show.image_url and show.slug and show.source:
                    local_path = await self._download_image(show.image_url, show.slug, show.source)
                    if local_path:
                        images_saved += 1
                        return show.model_copy(update={"local_image_path": local_path})
                return show

            image_tasks = [download_show_image(s) for s in result.items]
            shows_with_images = await asyncio.gather(*image_tasks, return_exceptions=True)
            shows_list = [s for s in shows_with_images if isinstance(s, ScrapeShow)]

            seen_slugs: set[str] = set()
            unique_shows: list[ScrapeShow] = []

            for show in shows_list:
                if show.detail_url and show.slug and show.slug not in seen_slugs:
                    seen_slugs.add(show.slug)
                    unique_shows.append(show)

            if max_items is not None:
                unique_shows = unique_shows[:max_items]

            logger.info("Total items to fetch details: %d", len(unique_shows))
            logger.info("Images saved from main page: %d", images_saved)

            semaphore = asyncio.Semaphore(max_concurrent)
            detail_wait_selector = origin.get_detail_wait_selector()
            successful_count = 0
            failed_count = 0

            async def fetch_detail(show: ScrapeShow) -> ScrapeShow:
                nonlocal successful_count, failed_count
                if not show.detail_url:
                    return show
                async with semaphore:
                    detail_page = await context.new_page()
                    try:
                        await detail_page.goto(show.detail_url, wait_until="domcontentloaded")
                        if detail_wait_selector:
                            with contextlib.suppress(Exception):
                                await detail_page.wait_for_selector(
                                    detail_wait_selector, timeout=10000
                                )
                        json_ld_check_js = """() => {
                            const scripts = document.querySelectorAll(
                                'script[type="application/ld+json"]'
                            );
                            for (const s of scripts) {
                                try {
                                    const data = JSON.parse(s.textContent);
                                    if (data['@type'] === 'Movie') return true;
                                    if (data['@type'] === 'TVSeries') return true;
                                } catch {}
                            }
                            return false;
                        }"""
                        with contextlib.suppress(Exception):
                            await detail_page.wait_for_function(json_ld_check_js, timeout=15000)
                        await asyncio.sleep(3)
                        detailed = await origin.extract_detail_page(detail_page, show)
                        if detailed and detailed.overview:
                            successful_count += 1
                            logger.debug("Extracted details for %s", show.slug)
                            return detailed
                        failed_count += 1
                        return show
                    except Exception as e:
                        failed_count += 1
                        logger.warning("Failed to fetch detail for %s: %s", show.slug, e)
                        return show
                    finally:
                        await detail_page.close()

            tasks = [fetch_detail(show) for show in unique_shows]
            detailed_shows = await asyncio.gather(*tasks, return_exceptions=True)

            valid_shows = [s for s in detailed_shows if isinstance(s, ScrapeShow)]

            logger.info(
                "Detail fetch complete - Successful: %d, Failed: %d", successful_count, failed_count
            )

            async def download_cast_images(show: ScrapeShow) -> ScrapeShow:
                if not show.cast:
                    return show
                updated_cast: list[ScrapeCastMember] = []
                for member in show.cast:
                    if member.image_url:
                        local_path = await self._download_cast_image(member.image_url, member.name)
                        updated_cast.append(
                            ScrapeCastMember(
                                name=member.name,
                                image_url=member.image_url,
                                local_image_path=local_path,
                            )
                        )
                    else:
                        updated_cast.append(member)
                return show.model_copy(update={"cast": updated_cast})

            cast_tasks = [download_cast_images(show) for show in valid_shows]
            shows_with_cast_images = await asyncio.gather(*cast_tasks, return_exceptions=True)
            final_shows = [s for s in shows_with_cast_images if isinstance(s, ScrapeShow)]

            return ScrapeShowList(items=final_shows)
        finally:
            await self._cleanup(p, browser, context)
