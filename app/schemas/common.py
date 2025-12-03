from pydantic import BaseModel, ConfigDict


class Genre(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str


class ImageVariant(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    link: str
    width: int
    height: int


class VerticalImageSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    w240: str
    w360: str
    w480: str
    w600: str
    w720: str


class HorizontalImageSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    w360: str
    w480: str
    w720: str
    w1080: str
    w1440: str


class ImageSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vertical_poster: VerticalImageSet | None = None
    horizontal_poster: HorizontalImageSet | None = None
    vertical_backdrop: VerticalImageSet | None = None
    horizontal_backdrop: HorizontalImageSet | None = None


class Price(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    amount: str
    currency: str
    formatted: str


class Locale(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    language: str
    region: str | None = None


class Subtitle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    locale: Locale
    closed_captions: bool = False


class ServiceImageSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    light_theme_image: str
    dark_theme_image: str
    white_image: str


class StreamingOptionTypes(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subscription: bool = False
    rent: bool = False
    buy: bool = False
    free: bool = False
    addon: bool = False


class Addon(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    home_page: str
    theme_color_code: str
    image_set: ServiceImageSet


class Service(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    home_page: str
    theme_color_code: str
    image_set: ServiceImageSet
    streaming_option_types: StreamingOptionTypes
    addons: list[Addon] | None = None
