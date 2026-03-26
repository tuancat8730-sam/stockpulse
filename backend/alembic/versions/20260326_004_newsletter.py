"""004 newsletter

Revision ID: 004
Revises: 003
Create Date: 2026-03-26

Tables: newsletter_campaigns, newsletter_sends, telegram_bot_events
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # newsletter_campaigns
    # ------------------------------------------------------------------
    op.create_table(
        "newsletter_campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("edition_type", sa.Text, nullable=False),
        sa.CheckConstraint("edition_type IN ('morning','evening')", name="ck_campaign_edition"),
        sa.Column("scheduled_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default="scheduled"),
        sa.CheckConstraint(
            "status IN ('scheduled','sending','sent','failed','cancelled')",
            name="ck_campaign_status",
        ),
        sa.Column("market_snapshot", postgresql.JSONB, nullable=True),
        sa.Column("global_snapshot", postgresql.JSONB, nullable=True),
        sa.Column("subject_line", sa.Text, nullable=True),
        sa.Column("preview_text", sa.Text, nullable=True),
        sa.Column("total_recipients", sa.Integer, nullable=True),
        sa.Column("total_sent", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_opened", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_failed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.create_index("idx_newsletter_campaigns_scheduled", "newsletter_campaigns", ["scheduled_at"])
    op.create_index("idx_newsletter_campaigns_status", "newsletter_campaigns", ["status"])
    op.execute(
        "CREATE TRIGGER trg_newsletter_campaigns_updated_at "
        "BEFORE UPDATE ON newsletter_campaigns "
        "FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();"
    )

    # ------------------------------------------------------------------
    # newsletter_sends
    # ------------------------------------------------------------------
    op.create_table(
        "newsletter_sends",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("newsletter_campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.Text, nullable=False, server_default="telegram"),
        sa.CheckConstraint("channel IN ('telegram','email')", name="ck_send_channel"),
        sa.Column("status", sa.Text, nullable=False, server_default="pending"),
        sa.CheckConstraint(
            "status IN ('pending','sent','delivered','failed','bounced')",
            name="ck_send_status",
        ),
        # Open tracking via inline keyboard button click
        sa.Column("open_token", sa.Text, unique=True, nullable=True),
        sa.Column("opened", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("opened_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("open_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("failed_reason", sa.Text, nullable=True),
        sa.UniqueConstraint("campaign_id", "user_id", "channel", name="uq_newsletter_send"),
    )
    op.create_index("idx_newsletter_sends_campaign_id", "newsletter_sends", ["campaign_id"])
    op.create_index("idx_newsletter_sends_user_id", "newsletter_sends", ["user_id"])
    op.create_index("idx_newsletter_sends_open_token", "newsletter_sends", ["open_token"],
                    postgresql_where=sa.text("open_token IS NOT NULL"))
    op.create_index("idx_newsletter_sends_status", "newsletter_sends", ["status"])

    # ------------------------------------------------------------------
    # telegram_bot_events
    # ------------------------------------------------------------------
    op.create_table(
        "telegram_bot_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("chat_id", sa.BigInteger, nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.CheckConstraint(
            "event_type IN ('start','login','logout','status',"
            "'bot_blocked','bot_unblocked','message_received','command_received')",
            name="ck_bot_event_type",
        ),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("occurred_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.create_index("idx_tg_bot_events_user_id", "telegram_bot_events", ["user_id"])
    op.create_index("idx_tg_bot_events_chat_id", "telegram_bot_events", ["chat_id"])
    op.create_index("idx_tg_bot_events_type", "telegram_bot_events", ["event_type"])
    op.create_index("idx_tg_bot_events_occurred", "telegram_bot_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_table("telegram_bot_events")
    op.drop_table("newsletter_sends")
    op.drop_table("newsletter_campaigns")
