"""Tests for Pydantic Settings validators."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings

# Minimal valid kwargs for Settings (no .env file involved)
_VALID_BASE = dict(
    app_env="development",
    app_secret_key="a" * 32,
    frontend_url="http://localhost:3000",
    database_url="postgresql://user:pw@localhost/db",
    supabase_url="https://x.supabase.co",
    supabase_anon_key="anon",
    supabase_service_role_key="role",
    google_client_id="gcid",
    google_client_secret="gcsecret",
    telegram_bot_token="123:token",
    redis_url="redis://localhost:6379",
    posthog_api_key="phc_test",
)


def _make(**overrides: object) -> Settings:
    return Settings.model_validate({**_VALID_BASE, **overrides})


# ------------------------------------------------------------------
# database_url validator
# ------------------------------------------------------------------

class TestDatabaseUrlValidator:
    def test_converts_postgresql_prefix(self) -> None:
        s = _make(database_url="postgresql://u:p@host/db")
        assert s.database_url.startswith("postgresql+asyncpg://")

    def test_converts_postgres_prefix(self) -> None:
        s = _make(database_url="postgres://u:p@host/db")
        assert s.database_url.startswith("postgresql+asyncpg://")

    def test_passthrough_asyncpg_url(self) -> None:
        s = _make(database_url="postgresql+asyncpg://u:p@host/db")
        assert s.database_url == "postgresql+asyncpg://u:p@host/db"

    def test_rejects_non_postgres_url(self) -> None:
        with pytest.raises(ValidationError, match="PostgreSQL"):
            _make(database_url="sqlite:///local.db")


# ------------------------------------------------------------------
# app_secret_key validator
# ------------------------------------------------------------------

class TestSecretKeyValidator:
    def test_accepts_key_of_exact_32_chars(self) -> None:
        s = _make(app_secret_key="x" * 32)
        assert len(s.app_secret_key) == 32

    def test_rejects_short_key(self) -> None:
        with pytest.raises(ValidationError, match="32 characters"):
            _make(app_secret_key="short")


# ------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------

class TestProperties:
    def test_is_production_false_in_development(self) -> None:
        s = _make(app_env="development")
        assert s.is_production is False
        assert s.is_development is True

    def test_is_production_true(self) -> None:
        s = _make(app_env="production")
        assert s.is_production is True
        assert s.is_development is False
