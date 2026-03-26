import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, Text, func, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

TIMESTAMPTZ = TIMESTAMP(timezone=True)


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)  # 'free'|'pro'|'premium'
    name: Mapped[str] = mapped_column(Text, nullable=False)
    price_vnd: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    billing_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    watchlist_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    alert_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    subscriptions: Mapped[list["UserSubscription"]] = relationship(back_populates="plan")

    def __repr__(self) -> str:
        return f"<SubscriptionPlan slug={self.slug} price={self.price_vnd}>"


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscription_plans.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_paid_vnd: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    plan: Mapped["SubscriptionPlan"] = relationship(back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<UserSubscription user={self.user_id} plan={self.plan_id} status={self.status}>"
