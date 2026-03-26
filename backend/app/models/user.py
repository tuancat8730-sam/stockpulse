import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Text, func, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

TIMESTAMPTZ = TIMESTAMP(timezone=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Google OAuth
    google_id: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Telegram binding
    telegram_chat_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, nullable=True
    )
    telegram_username: Mapped[str | None] = mapped_column(Text, nullable=True)
    telegram_linked_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)

    # Account state
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)

    # Referral
    referral_code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    referred_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    bonus_watchlist_slots: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # NPS
    nps_eligible_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    nps_sent_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    onboarding_tokens: Mapped[list["TelegramOnboardingToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    watchlist_items: Mapped[list["WatchlistItem"]] = relationship(  # type: ignore[name-defined]
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class OAuthSession(Base):
    __tablename__ = "oauth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    state: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    redirect_to: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<OAuthSession state={self.state[:8]}...>"


class TelegramOnboardingToken(Base):
    """
    One-time token linking a Telegram chat to a Google account.

    IMPORTANT: user_id is nullable — the token is created BEFORE the user
    completes Google OAuth. Once OAuth succeeds, user_id is populated.
    telegram_chat_id is stored here (not in schema.sql original) so the bot
    can identify which chat to notify after linking completes.
    """

    __tablename__ = "telegram_onboarding_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # nullable: populated after Google OAuth completes
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    # Added vs original schema: stores chat_id before user row exists
    telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )

    # Relationship (optional, only populated after linking)
    user: Mapped["User | None"] = relationship(back_populates="onboarding_tokens")

    def __repr__(self) -> str:
        return f"<TelegramOnboardingToken token={self.token[:8]}... used={self.used}>"
