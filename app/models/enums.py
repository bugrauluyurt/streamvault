import enum


class ShowType(str, enum.Enum):
    MOVIE = "movie"
    SERIES = "series"


class ItemType(str, enum.Enum):
    SHOW = "show"
    SEASON = "season"
    EPISODE = "episode"


class StreamingOptionType(str, enum.Enum):
    SUBSCRIPTION = "subscription"
    FREE = "free"
    RENT = "rent"
    BUY = "buy"
    ADDON = "addon"


class Quality(str, enum.Enum):
    SD = "sd"
    HD = "hd"
    QHD = "qhd"
    UHD = "uhd"


class ChangeType(str, enum.Enum):
    NEW = "new"
    REMOVED = "removed"
    UPDATED = "updated"
    EXPIRING = "expiring"
    UPCOMING = "upcoming"
