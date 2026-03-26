"""001 auth users

Revision ID: 001
Revises:
Create Date: 2026-03-26

Tables: users, oauth_sessions, telegram_onboarding_tokens
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # updated_at trigger function (shared utility)
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION trigger_set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        # Google OAuth
        sa.Column("google_id", sa.Text, unique=True, nullable=True),
        sa.Column("email", sa.Text, unique=True, nullable=False),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("full_name", sa.Text, nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        # Telegram binding
        sa.Column("telegram_chat_id", sa.BigInteger, unique=True, nullable=True),
        sa.Column("telegram_username", sa.Text, nullable=True),
        sa.Column("telegram_linked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Account state
        sa.Column("status", sa.Text, nullable=False, server_default="active"),
        sa.CheckConstraint("status IN ('active', 'suspended', 'deactivated')", name="ck_users_status"),
        # Soft delete
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Referral
        sa.Column("referral_code", sa.Text, unique=True, nullable=False,
                  server_default=sa.text("substr(md5(gen_random_uuid()::text), 1, 8)")),
        sa.Column("referred_by_user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bonus_watchlist_slots", sa.Integer, nullable=False, server_default="0"),
        sa.CheckConstraint("bonus_watchlist_slots >= 0", name="ck_users_bonus_slots"),
        # NPS
        sa.Column("nps_eligible_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("nps_sent_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.create_index("idx_users_email", "users", ["email"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_users_google_id", "users", ["google_id"],
                    postgresql_where=sa.text("google_id IS NOT NULL"))
    op.create_index("idx_users_telegram_chat_id", "users", ["telegram_chat_id"],
                    postgresql_where=sa.text("telegram_chat_id IS NOT NULL"))
    op.create_index("idx_users_referred_by", "users", ["referred_by_user_id"],
                    postgresql_where=sa.text("referred_by_user_id IS NOT NULL"))
    op.create_index("idx_users_referral_code", "users", ["referral_code"])
    op.create_index("idx_users_deleted_at", "users", ["deleted_at"],
                    postgresql_where=sa.text("deleted_at IS NOT NULL"))
    op.execute(
        "CREATE TRIGGER trg_users_updated_at "
        "BEFORE UPDATE ON users "
        "FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();"
    )

    # ------------------------------------------------------------------
    # oauth_sessions
    # ------------------------------------------------------------------
    op.create_table(
        "oauth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("state", sa.Text, unique=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("redirect_to", sa.Text, nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.create_index("idx_oauth_sessions_state", "oauth_sessions", ["state"])
    op.create_index("idx_oauth_sessions_expires_at", "oauth_sessions", ["expires_at"])

    # ------------------------------------------------------------------
    # telegram_onboarding_tokens
    # IMPORTANT: user_id is nullable (populated after Google OAuth completes)
    # telegram_chat_id added vs original schema to store chat before user exists
    # ------------------------------------------------------------------
    op.create_table(
        "telegram_onboarding_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("telegram_chat_id", sa.BigInteger, nullable=True),
        sa.Column("token", sa.Text, unique=True, nullable=False),
        sa.Column("used", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.create_index("idx_tg_onboarding_tokens_token", "telegram_onboarding_tokens", ["token"],
                    postgresql_where=sa.text("NOT used"))
    op.create_index("idx_tg_onboarding_tokens_user_id", "telegram_onboarding_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_table("telegram_onboarding_tokens")
    op.drop_table("oauth_sessions")
    op.drop_table("users")
    op.execute("DROP FUNCTION IF EXISTS trigger_set_updated_at() CASCADE;")
