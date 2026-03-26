from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, Numeric, Text, func, TIMESTAMP

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

TIMESTAMPTZ = TIMESTAMP(timezone=True)


class StockTicker(Base):
    """Master reference list of all listed securities (HOSE/HNX/UPCOM)."""

    __tablename__ = "stock_tickers"

    ticker: Mapped[str] = mapped_column(Text, primary_key=True)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    exchange: Mapped[str] = mapped_column(Text, nullable=False)  # 'HOSE'|'HNX'|'UPCOM'
    sector: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(Text, nullable=True)
    market_cap_vnd: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    listed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    delisted_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<StockTicker {self.ticker} ({self.exchange})>"
