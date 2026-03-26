"""006 analytics

Revision ID: 006
Revises: 005
Create Date: 2026-03-26

Tables: analytics_events
Append-only event stream — no UPDATE/DELETE after insert.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None

# All 21 tracked event names
_VALID_EVENTS = (
    "'user_registered','google_oauth_completed','telegram_linked','onboarding_completed',"
    "'bot_start_command','bot_login_command','bot_status_command','bot_blocked','bot_unblocked',"
    "'newsletter_sent','newsletter_opened','newsletter_link_clicked',"
    "'alert_created','alert_triggered',"
    "'subscription_started','subscription_cancelled',"
    "'payment_initiated','payment_completed','payment_failed',"
    "'post_published','referral_completed'"
)


def upgrade() -> None:
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_id", sa.Text, nullable=True),
        sa.Column("event_name", sa.Text, nullable=False),
        sa.CheckConstraint(f"event_name IN ({_VALID_EVENTS})", name="ck_analytics_event_name"),
        sa.Column("properties", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("platform", sa.Text, nullable=False, server_default="telegram"),
        sa.CheckConstraint("platform IN ('web','telegram','api')", name="ck_analytics_platform"),
        sa.Column("ip_address", sa.Text, nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("occurred_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.create_index("idx_analytics_user_id", "analytics_events", ["user_id"],
                    postgresql_where=sa.text("user_id IS NOT NULL"))
    op.create_index("idx_analytics_event_name", "analytics_events", ["event_name"])
    op.create_index("idx_analytics_occurred_at", "analytics_events", ["occurred_at"],
                    postgresql_ops={"occurred_at": "DESC"})
    op.create_index("idx_analytics_session_id", "analytics_events", ["session_id"],
                    postgresql_where=sa.text("session_id IS NOT NULL"))
    op.create_index("idx_analytics_properties", "analytics_events",
                    ["properties"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_table("analytics_events")
