from .base import SiteOrigin
from .justwatch import SiteOriginJustWatch

SITE_ORIGINS: dict[str, type[SiteOrigin]] = {
    "justwatch": SiteOriginJustWatch,
}


def get_site_origin(origin: str) -> SiteOrigin:
    origin_class = SITE_ORIGINS.get(origin)
    if origin_class is None:
        raise ValueError(f"Unknown site origin: {origin}")
    return origin_class()
