from enum import StrEnum


class ShowType(StrEnum):
    MOVIE = "movie"
    SERIES = "series"


class ItemType(StrEnum):
    SHOW = "show"
    SEASON = "season"
    EPISODE = "episode"


class StreamingOptionType(StrEnum):
    SUBSCRIPTION = "subscription"
    FREE = "free"
    RENT = "rent"
    BUY = "buy"
    ADDON = "addon"


class Quality(StrEnum):
    SD = "sd"
    HD = "hd"
    QHD = "qhd"
    UHD = "uhd"


class ChangeType(StrEnum):
    NEW = "new"
    REMOVED = "removed"
    UPDATED = "updated"
    EXPIRING = "expiring"
    UPCOMING = "upcoming"
