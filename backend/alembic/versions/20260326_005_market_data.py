"""005 market data

Revision ID: 005
Revises: 004
Create Date: 2026-03-26

Tables: stock_tickers
Note: eod_prices, technical_indicators, market_index_eod, foreign_investor_flow,
      global_market_indicators, corporate_events are deferred to Sprint 1 (Task 1.3)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stock_tickers",
        sa.Column("ticker", sa.Text, primary_key=True),
        sa.Column("company_name", sa.Text, nullable=False),
        sa.Column("exchange", sa.Text, nullable=False),
        sa.CheckConstraint("exchange IN ('HOSE','HNX','UPCOM')", name="ck_ticker_exchange"),
        sa.Column("sector", sa.Text, nullable=True),
        sa.Column("industry", sa.Text, nullable=True),
        sa.Column("market_cap_vnd", sa.Numeric(20, 2), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("listed_at", sa.Date, nullable=True),
        sa.Column("delisted_at", sa.Date, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
    )
    op.create_index("idx_tickers_exchange", "stock_tickers", ["exchange"],
                    postgresql_where=sa.text("is_active = true"))
    op.create_index("idx_tickers_sector", "stock_tickers", ["sector"],
                    postgresql_where=sa.text("is_active = true"))
    op.execute(
        "CREATE TRIGGER trg_stock_tickers_updated_at "
        "BEFORE UPDATE ON stock_tickers "
        "FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();"
    )


def downgrade() -> None:
    op.drop_table("stock_tickers")
