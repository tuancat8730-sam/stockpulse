"""UserRepository — all DB operations for the users table.

Follows immutable-return convention: methods never mutate the caller's
objects; they always return freshly-loaded ORM instances from the DB.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@dataclass(frozen=True)
class CreateUserData:
    email: str
    google_id: str
    full_name: str | None = None
    avatar_url: str | None = None
    email_verified: bool = False
    referral_code: str | None = None
    referred_by_user_id: uuid.UUID | None = None


@dataclass(frozen=True)
class TelegramLinkData:
    telegram_chat_id: int
    telegram_username: str | None = None


class UserRepository:
    """Encapsulates all DB access for :class:`~app.models.user.User`.

    Pass an :class:`AsyncSession` that is managed (commit/rollback) by the
    caller — typically via :func:`app.core.database.get_session`.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def find_by_google_id(self, google_id: str) -> User | None:
        """Return the active (non-deleted) user with this Google sub, or None."""
        result = await self._session.execute(
            select(User).where(
                User.google_id == google_id,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def find_by_telegram_chat_id(self, telegram_chat_id: int) -> User | None:
        """Return the active user bound to this Telegram chat, or None."""
        result = await self._session.execute(
            select(User).where(
                User.telegram_chat_id == telegram_chat_id,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def find_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return the user with this PK, or None."""
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        """Return the active user with this e-mail, or None."""
        result = await self._session.execute(
            select(User).where(
                User.email == email,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Mutations — always return a freshly-loaded instance
    # ------------------------------------------------------------------

    async def create(self, data: CreateUserData) -> User:
        """Insert a new user row and return the persisted instance.

        The caller must commit (or rely on the session context manager to
        commit) after this call.
        """
        referral_code = data.referral_code or _generate_referral_code()
        user = User(
            email=data.email,
            google_id=data.google_id,
            full_name=data.full_name,
            avatar_url=data.avatar_url,
            email_verified=data.email_verified,
            referral_code=referral_code,
            referred_by_user_id=data.referred_by_user_id,
        )
        self._session.add(user)
        await self._session.flush()   # obtain PK without committing
        await self._session.refresh(user)
        return user

    async def update_telegram_link(
        self,
        user_id: uuid.UUID,
        link: TelegramLinkData,
    ) -> User:
        """Bind a Telegram chat to the user and return the updated instance.

        Raises :exc:`ValueError` if the user is not found.
        """
        user = await self.find_by_id(user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")

        user.telegram_chat_id = link.telegram_chat_id
        user.telegram_username = link.telegram_username
        user.telegram_linked_at = datetime.now(tz=timezone.utc)

        await self._session.flush()
        await self._session.refresh(user)
        return user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_referral_code() -> str:
    """8-char hex referral code, same entropy as the DB default."""
    return uuid.uuid4().hex[:8]
