"""003 watchlist

Revision ID: 003
Revises: 002
Create Date: 2026-03-26

Tables: watchlist_items
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "watchlist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ticker", sa.Text, nullable=False),
        sa.Column("added_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "ticker", name="uq_watchlist_user_ticker"),
    )
    op.create_index("idx_watchlist_user_id", "watchlist_items", ["user_id"])
    op.create_index("idx_watchlist_ticker", "watchlist_items", ["ticker"])


def downgrade() -> None:
    op.drop_table("watchlist_items")
