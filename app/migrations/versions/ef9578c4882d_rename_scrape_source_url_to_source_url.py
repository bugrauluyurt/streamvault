"""rename scrape_source_url to source_url

Revision ID: ef9578c4882d
Revises: a5b87172c4fb
Create Date: 2025-12-06 20:24:16.635634

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ef9578c4882d"
down_revision: str | None = "a5b87172c4fb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("scraped", "scrape_source_url", new_column_name="source_url")


def downgrade() -> None:
    op.alter_column("scraped", "source_url", new_column_name="scrape_source_url")
