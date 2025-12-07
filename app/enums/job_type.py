from enum import StrEnum


class JobType(StrEnum):
    SCRAPE_TOP_TEN = "scrape_top_ten"
    SCRAPE_POPULAR = "scrape_popular"
    ENRICH_TMDB = "enrich_tmdb"
