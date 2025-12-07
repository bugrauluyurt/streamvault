"""rename scraped to scraped_shows

Revision ID: ee91dc87304d
Revises: 708963fd497d
Create Date: 2025-12-06 22:09:27.941188

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ee91dc87304d"
down_revision: str | None = "708963fd497d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("scraped", "scraped_shows")

    op.create_table(
        "scraped_top_shows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("show_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("show_type", sa.String(), nullable=False),
        sa.Column("batch_sequence", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["show_id"], ["scraped_shows.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_scraped_top_shows_batch_sequence",
        "scraped_top_shows",
        ["batch_sequence"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_scraped_top_shows_batch_sequence", table_name="scraped_top_shows")
    op.drop_table("scraped_top_shows")
    op.rename_table("scraped_shows", "scraped")
