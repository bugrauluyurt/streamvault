from collections.abc import Awaitable, Callable

from app.enums import JobType
from app.models import Job

from .scrape_handlers import handle_scrape_popular, handle_scrape_top_ten

JobHandler = Callable[[Job], Awaitable[dict]]

HANDLERS: dict[JobType, JobHandler] = {
    JobType.SCRAPE_TOP_TEN: handle_scrape_top_ten,
    JobType.SCRAPE_POPULAR: handle_scrape_popular,
}
