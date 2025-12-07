import json
import logging

from langchain_core.exceptions import OutputParserException
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import ScrapedType, ValidationStatus
from app.models import Job, ScrapedPopularShow, ScrapedShow, ScrapedTopShow
from app.schemas.tmdb import TMDBMovieSearchResult, TMDBTVSearchResult
from app.schemas.validation import TMDBValidationResult
from app.services.llm_service import LLMService
from app.services.tmdb_service import TMDBService

logger = logging.getLogger(__name__)

MAX_LLM_RETRIES = 3


def _extract_essential_details(details: dict | None) -> dict:
    if not details:
        return {}
    genres = details.get("genres") or []
    cast = details.get("cast") or []
    return {
        "title": details.get("title"),
        "overview": details.get("overview"),
        "release_year": details.get("release_year"),
        "first_air_year": details.get("first_air_year"),
        "genres": [g.get("name") for g in genres if isinstance(g, dict) and g.get("name")],
        "directors": details.get("directors") or [],
        "cast": [c.get("name") for c in cast[:5] if isinstance(c, dict) and c.get("name")],
        "runtime": details.get("runtime"),
        "rating": details.get("rating"),
    }


def _format_movie_results(results: list[TMDBMovieSearchResult]) -> str:
    formatted: list[str] = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"{i}. TMDB ID: {r.id}\n"
            f"   Title: {r.title}\n"
            f"   Original Title: {r.original_title or 'N/A'}\n"
            f"   Release Date: {r.release_date or 'N/A'}\n"
            f"   Overview: {r.overview or 'N/A'}\n"
            f"   Vote Average: {r.vote_average or 'N/A'}\n"
            f"   Popularity: {r.popularity or 'N/A'}"
        )
    return "\n\n".join(formatted)


def _format_tv_results(results: list[TMDBTVSearchResult]) -> str:
    formatted: list[str] = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"{i}. TMDB ID: {r.id}\n"
            f"   Name: {r.name}\n"
            f"   Original Name: {r.original_name or 'N/A'}\n"
            f"   First Air Date: {r.first_air_date or 'N/A'}\n"
            f"   Overview: {r.overview or 'N/A'}\n"
            f"   Vote Average: {r.vote_average or 'N/A'}\n"
            f"   Popularity: {r.popularity or 'N/A'}"
        )
    return "\n\n".join(formatted)


async def handle_validate_and_store(job: Job, db: AsyncSession) -> dict:
    source_table = job.payload.get("source_table", "popular_shows")
    reprocess = job.payload.get("reprocess", False)

    status_filter = ValidationStatus.PROCESSED if reprocess else ValidationStatus.NOT_STARTED

    if source_table == "top_shows":
        query = (
            select(ScrapedTopShow)
            .where(ScrapedTopShow.validation_status == status_filter)
            .where(ScrapedTopShow.tmdb_id.is_(None))
            .order_by(ScrapedTopShow.created_at.desc())
        )
    else:
        query = (
            select(ScrapedPopularShow)
            .where(ScrapedPopularShow.validation_status == status_filter)
            .where(ScrapedPopularShow.tmdb_id.is_(None))
            .order_by(ScrapedPopularShow.created_at.desc())
        )

    items = (await db.execute(query)).scalars().all()

    if not items:
        return {
            "source_table": source_table,
            "processed": 0,
            "validated": 0,
            "needs_review": 0,
            "skipped": 0,
            "message": f"No items with status '{status_filter}' found",
        }

    tmdb = TMDBService()
    llm = LLMService()

    validated = 0
    skipped = 0
    needs_review_count = 0

    try:
        for item in items:
            details: dict = item.details
            title = details.get("title", "")
            show_type = details.get("show_type", "movie")

            if not title:
                logger.warning("Item %d has no title, skipping", item.id)
                skipped += 1
                continue

            logger.info("Processing: %s (%s)", title, show_type)

            try:
                if show_type == "movie":
                    search_response = await tmdb.search_movies(title)
                    if not search_response.results:
                        logger.info("No TMDB results for movie: %s", title)
                        skipped += 1
                        continue
                    tmdb_candidates = _format_movie_results(search_response.results[:5])
                else:
                    search_response = await tmdb.search_tv(title)
                    if not search_response.results:
                        logger.info("No TMDB results for TV show: %s", title)
                        skipped += 1
                        continue
                    tmdb_candidates = _format_tv_results(search_response.results[:5])

                essential_details = _extract_essential_details(details)
                prompt = (
                    "Match this show to the best TMDB candidate.\n\n"
                    f"SHOW: {json.dumps(essential_details)}\n\n"
                    f"CANDIDATES:\n{tmdb_candidates}\n\n"
                    "Pick the best matching tmdb_id. Rate confidence 1-10."
                )

                result: TMDBValidationResult | None = None
                for attempt in range(MAX_LLM_RETRIES):
                    try:
                        result = await llm.extract_structured(prompt, TMDBValidationResult)
                        break
                    except OutputParserException as e:
                        llm_output = getattr(e, "llm_output", None)
                        logger.warning(
                            "LLM parse error for %s (attempt %d/%d): %s\nLLM output: %s",
                            title,
                            attempt + 1,
                            MAX_LLM_RETRIES,
                            str(e)[:200],
                            llm_output,
                        )
                        if attempt == MAX_LLM_RETRIES - 1:
                            raise

                if result is None:
                    logger.error("Failed to get LLM result for %s after retries", title)
                    skipped += 1
                    continue

                tmdb_id_str = str(result.tmdb_id)

                new_status = (
                    ValidationStatus.REPROCESSED if reprocess else ValidationStatus.PROCESSED
                )

                needs_review = result.confidence < 8

                stmt = pg_insert(ScrapedShow).values(
                    tmdb_id=tmdb_id_str,
                    name=title,
                    details=details,
                    type=ScrapedType(show_type),
                    source_url=details.get("detail_url", ""),
                    needs_review=needs_review,
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=["tmdb_id"],
                    set_={
                        "name": stmt.excluded.name,
                        "details": stmt.excluded.details,
                        "type": stmt.excluded.type,
                        "source_url": stmt.excluded.source_url,
                        "needs_review": stmt.excluded.needs_review,
                        "updated_at": func.now(),
                    },
                )
                await db.execute(stmt)

                item.tmdb_id = tmdb_id_str
                item.confidence = result.confidence
                item.validation_status = new_status
                await db.flush()

                if needs_review:
                    needs_review_count += 1
                    logger.info(
                        "Stored with review flag: %s -> TMDB %d (confidence: %d/10) - %s",
                        title,
                        result.tmdb_id,
                        result.confidence,
                        result.reasoning,
                    )
                else:
                    validated += 1
                    logger.info(
                        "Validated: %s -> TMDB %d (confidence: %d/10)",
                        title,
                        result.tmdb_id,
                        result.confidence,
                    )

            except Exception as e:
                logger.exception("Error processing %s: %s", title, e)
                skipped += 1
                continue

    finally:
        await tmdb.close()

    return {
        "source_table": source_table,
        "processed": len(items),
        "validated": validated,
        "needs_review": needs_review_count,
        "skipped": skipped,
    }
