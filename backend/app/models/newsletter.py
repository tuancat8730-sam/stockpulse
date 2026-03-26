import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Text, UniqueConstraint, func, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

TIMESTAMPTZ = TIMESTAMP(timezone=True)


class NewsletterCampaign(Base):
    __tablename__ = "newsletter_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    edition_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'morning'|'evening'
    scheduled_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="scheduled")

    market_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    global_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    subject_line: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    total_recipients: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_sent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_opened: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    sends: Mapped[list["NewsletterSend"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<NewsletterCampaign type={self.edition_type} scheduled={self.scheduled_at}>"


class NewsletterSend(Base):
    __tablename__ = "newsletter_sends"
    __table_args__ = (
        UniqueConstraint("campaign_id", "user_id", "channel", name="uq_newsletter_send"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("newsletter_campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(Text, nullable=False, default="telegram")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")

    # Open tracking via inline keyboard button click
    open_token: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    opened: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    opened_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    open_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    sent_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    failed_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaign: Mapped["NewsletterCampaign"] = relationship(back_populates="sends")

    def __repr__(self) -> str:
        return f"<NewsletterSend campaign={self.campaign_id} user={self.user_id} status={self.status}>"


class TelegramBotEvent(Base):
    """Records bot lifecycle events for audit and analytics."""

    __tablename__ = "telegram_bot_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<TelegramBotEvent type={self.event_type} chat={self.chat_id}>"
