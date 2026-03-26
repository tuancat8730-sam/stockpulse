import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text, func, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

TIMESTAMPTZ = TIMESTAMP(timezone=True)


class AnalyticsEvent(Base):
    """
    Append-only event stream. No UPDATE/DELETE — immutable audit log.
    21 tracked events covering onboarding, bot, newsletter, alerts,
    subscription, community, and referral flows.
    """

    __tablename__ = "analytics_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    session_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_name: Mapped[str] = mapped_column(Text, nullable=False)
    properties: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    platform: Mapped[str] = mapped_column(Text, nullable=False, default="telegram")
    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<AnalyticsEvent event={self.event_name} user={self.user_id}>"
