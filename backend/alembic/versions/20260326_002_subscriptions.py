"""002 subscriptions

Revision ID: 002
Revises: 001
Create Date: 2026-03-26

Tables: subscription_plans (+ seed data), user_subscriptions
"""

import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # subscription_plans
    # ------------------------------------------------------------------
    op.create_table(
        "subscription_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.Text, unique=True, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("price_vnd", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.CheckConstraint("price_vnd >= 0", name="ck_plans_price"),
        sa.Column("billing_period_days", sa.Integer, nullable=False, server_default="30"),
        sa.CheckConstraint("billing_period_days > 0", name="ck_plans_period"),
        sa.Column("watchlist_limit", sa.Integer, nullable=False, server_default="3"),
        sa.CheckConstraint("watchlist_limit > 0 OR watchlist_limit = -1", name="ck_plans_wl_limit"),
        sa.Column("alert_limit", sa.Integer, nullable=False, server_default="0"),
        sa.CheckConstraint("alert_limit >= 0 OR alert_limit = -1", name="ck_plans_alert_limit"),
        sa.Column("features", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.execute(
        "CREATE TRIGGER trg_subscription_plans_updated_at "
        "BEFORE UPDATE ON subscription_plans "
        "FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();"
    )

    # Seed plans (idempotent) — use parameterized insert to avoid `:true`/`:false`
    # being mis-parsed as SQLAlchemy bind parameters
    _INSERT_PLAN = sa.text(
        "INSERT INTO subscription_plans"
        " (slug, name, price_vnd, billing_period_days, watchlist_limit, alert_limit, features)"
        " VALUES (:slug, :name, :price_vnd, :billing_period_days, :watchlist_limit,"
        "         :alert_limit, cast(:features AS jsonb))"
        " ON CONFLICT (slug) DO NOTHING"
    )
    _PLANS = [
        {
            "slug": "free", "name": "Free", "price_vnd": 0,
            "billing_period_days": 30, "watchlist_limit": 3, "alert_limit": 0,
            "features": json.dumps({
                "morning_newsletter": True, "evening_newsletter": False, "ai_news": False,
                "price_alerts": False, "rsi_alerts": False, "volume_alerts": False,
                "technical_analysis": False, "global_indicators": False, "web_dashboard": False,
            }),
        },
        {
            "slug": "pro", "name": "Pro", "price_vnd": 99000,
            "billing_period_days": 30, "watchlist_limit": 10, "alert_limit": 10,
            "features": json.dumps({
                "morning_newsletter": True, "evening_newsletter": True, "ai_news": True,
                "price_alerts": True, "rsi_alerts": False, "volume_alerts": False,
                "technical_analysis": False, "global_indicators": False, "web_dashboard": True,
            }),
        },
        {
            "slug": "premium", "name": "Premium", "price_vnd": 299000,
            "billing_period_days": 30, "watchlist_limit": -1, "alert_limit": -1,
            "features": json.dumps({
                "morning_newsletter": True, "evening_newsletter": True, "ai_news": True,
                "price_alerts": True, "rsi_alerts": True, "volume_alerts": True,
                "technical_analysis": True, "global_indicators": True, "web_dashboard": True,
            }),
        },
    ]
    conn = op.get_bind()
    for plan in _PLANS:
        conn.execute(_INSERT_PLAN, plan)

    # ------------------------------------------------------------------
    # user_subscriptions
    # ------------------------------------------------------------------
    op.create_table(
        "user_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("subscription_plans.id"), nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="active"),
        sa.CheckConstraint(
            "status IN ('active','cancelled','expired','past_due','trialing')",
            name="ck_user_sub_status",
        ),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("cancel_reason", sa.Text, nullable=True),
        sa.Column("price_paid_vnd", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.create_index("idx_user_subscriptions_user_id", "user_subscriptions", ["user_id"])
    op.create_index("idx_user_subscriptions_plan_id", "user_subscriptions", ["plan_id"])
    op.create_index("idx_user_subscriptions_status", "user_subscriptions", ["status"])
    op.create_index("idx_user_subscriptions_expires_at", "user_subscriptions", ["expires_at"],
                    postgresql_where=sa.text("status = 'active'"))
    op.execute(
        "CREATE TRIGGER trg_user_subscriptions_updated_at "
        "BEFORE UPDATE ON user_subscriptions "
        "FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();"
    )


def downgrade() -> None:
    op.drop_table("user_subscriptions")
    op.drop_table("subscription_plans")
