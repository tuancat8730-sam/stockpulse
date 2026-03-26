"""Unit tests for UserRepository.

Each test runs in an isolated DB transaction (see conftest.py) that is
rolled back after the test — no manual cleanup required.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import (
    CreateUserData,
    TelegramLinkData,
    UserRepository,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_create_data(**overrides: object) -> CreateUserData:
    defaults: dict[str, object] = {
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
        "google_id": f"google_{uuid.uuid4().hex[:12]}",
        "full_name": "Test User",
        "avatar_url": None,
        "email_verified": True,
    }
    defaults.update(overrides)
    return CreateUserData(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------

class TestCreate:
    async def test_returns_persisted_user(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        data = _make_create_data()

        user = await repo.create(data)

        assert user.id is not None
        assert user.email == data.email
        assert user.google_id == data.google_id
        assert user.full_name == data.full_name
        assert user.email_verified is True
        assert user.status == "active"
        assert user.telegram_chat_id is None

    async def test_generates_referral_code(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        user = await repo.create(_make_create_data())

        assert user.referral_code is not None
        assert len(user.referral_code) == 8

    async def test_custom_referral_code(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        user = await repo.create(_make_create_data(referral_code="abcd1234"))

        assert user.referral_code == "abcd1234"

    async def test_referral_link(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        referrer = await repo.create(_make_create_data())
        referred = await repo.create(
            _make_create_data(referred_by_user_id=referrer.id)
        )

        assert referred.referred_by_user_id == referrer.id

    async def test_duplicate_email_raises(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        data = _make_create_data()
        await repo.create(data)

        with pytest.raises(Exception):
            await repo.create(_make_create_data(email=data.email))

    async def test_duplicate_google_id_raises(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        data = _make_create_data()
        await repo.create(data)

        with pytest.raises(Exception):
            await repo.create(_make_create_data(google_id=data.google_id))


# ---------------------------------------------------------------------------
# find_by_google_id()
# ---------------------------------------------------------------------------

class TestFindByGoogleId:
    async def test_returns_existing_user(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        created = await repo.create(_make_create_data())

        found = await repo.find_by_google_id(created.google_id)  # type: ignore[arg-type]

        assert found is not None
        assert found.id == created.id

    async def test_returns_none_for_unknown(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)

        result = await repo.find_by_google_id("no_such_google_id")

        assert result is None


# ---------------------------------------------------------------------------
# find_by_telegram_chat_id()
# ---------------------------------------------------------------------------

class TestFindByTelegramChatId:
    async def test_returns_none_before_linking(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        await repo.create(_make_create_data())

        result = await repo.find_by_telegram_chat_id(999_999_999)

        assert result is None

    async def test_returns_user_after_linking(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        created = await repo.create(_make_create_data())
        await repo.update_telegram_link(
            created.id, TelegramLinkData(telegram_chat_id=42_000_001, telegram_username="tester")
        )

        found = await repo.find_by_telegram_chat_id(42_000_001)

        assert found is not None
        assert found.id == created.id


# ---------------------------------------------------------------------------
# update_telegram_link()
# ---------------------------------------------------------------------------

class TestUpdateTelegramLink:
    async def test_sets_chat_id_and_timestamp(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        created = await repo.create(_make_create_data())

        updated = await repo.update_telegram_link(
            created.id,
            TelegramLinkData(telegram_chat_id=123_456_789, telegram_username="tguser"),
        )

        assert updated.telegram_chat_id == 123_456_789
        assert updated.telegram_username == "tguser"
        assert updated.telegram_linked_at is not None

    async def test_chat_id_without_username(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        created = await repo.create(_make_create_data())

        updated = await repo.update_telegram_link(
            created.id,
            TelegramLinkData(telegram_chat_id=777_000_001),
        )

        assert updated.telegram_chat_id == 777_000_001
        assert updated.telegram_username is None

    async def test_raises_for_unknown_user(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.update_telegram_link(
                uuid.uuid4(),
                TelegramLinkData(telegram_chat_id=1),
            )

    async def test_duplicate_chat_id_raises(self, db_session: AsyncSession) -> None:
        """Two users cannot share the same telegram_chat_id (unique constraint)."""
        repo = UserRepository(db_session)
        user_a = await repo.create(_make_create_data())
        user_b = await repo.create(_make_create_data())

        await repo.update_telegram_link(
            user_a.id, TelegramLinkData(telegram_chat_id=555_000_001)
        )

        with pytest.raises(Exception):
            await repo.update_telegram_link(
                user_b.id, TelegramLinkData(telegram_chat_id=555_000_001)
            )


# ---------------------------------------------------------------------------
# find_by_email() / find_by_id()
# ---------------------------------------------------------------------------

class TestFindHelpers:
    async def test_find_by_email(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        created = await repo.create(_make_create_data())

        found = await repo.find_by_email(created.email)

        assert found is not None
        assert found.id == created.id

    async def test_find_by_email_returns_none(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)

        assert await repo.find_by_email("nobody@example.com") is None

    async def test_find_by_id(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        created = await repo.create(_make_create_data())

        found = await repo.find_by_id(created.id)

        assert found is not None
        assert found.email == created.email

    async def test_find_by_id_returns_none(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)

        assert await repo.find_by_id(uuid.uuid4()) is None
