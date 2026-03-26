"""AuthService — Google OAuth 2.0 flow for Telegram-linked accounts.

Flow:
  1. Bot calls begin_login(chat_id) → receives a Google OAuth URL.
  2. User opens URL in browser, authenticates with Google.
  3. Google redirects to /api/auth/callback?code=…&state=…
  4. handle_callback(code, state, session) exchanges code, upserts the user,
     binds telegram_chat_id, and returns the linked user + chat_id.
"""

from __future__ import annotations

import base64
import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.models.user import OAuthSession, TelegramOnboardingToken, User
from app.repositories.user_repo import CreateUserData, TelegramLinkData, UserRepository

# Google OAuth endpoints (well-known, no env needed)
_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"  # noqa: S105

_ONBOARDING_TTL_MINUTES = 10
_OAUTH_SESSION_TTL_MINUTES = 15


# ---------------------------------------------------------------------------
# Public result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BeginLoginResult:
    """Returned by begin_login; pass google_url to the user."""
    google_url: str
    link_token: str          # opaque token stored in telegram_onboarding_tokens


@dataclass(frozen=True)
class CallbackResult:
    """Returned by handle_callback after successful OAuth."""
    user: User
    telegram_chat_id: int | None   # None if state had no linked onboarding token


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AuthError(Exception):
    """Raised for recoverable auth failures (expired state, bad code, etc.)."""


# ---------------------------------------------------------------------------
# AuthService
# ---------------------------------------------------------------------------

class AuthService:
    """Stateless OAuth service — all state lives in the DB.

    Pass the :class:`AsyncSession` per-request; the session's transaction
    is managed by the caller (FastAPI dependency / test fixture).
    """

    def __init__(self, settings: Settings, session: AsyncSession) -> None:
        self._settings = settings
        self._session = session
        self._repo = UserRepository(session)

    # ------------------------------------------------------------------
    # Step 1: Bot calls this to generate the login URL
    # ------------------------------------------------------------------

    async def begin_login(self, telegram_chat_id: int) -> BeginLoginResult:
        """Create an onboarding token and build the Google OAuth URL.

        The returned ``link_token`` is sent to the user as a URL parameter
        so the callback can identify which Telegram chat to notify.
        """
        link_token = secrets.token_urlsafe(32)
        csrf_state = secrets.token_urlsafe(32)
        now = datetime.now(tz=timezone.utc)

        # Persist the onboarding token (user_id=NULL until OAuth completes)
        onboarding = TelegramOnboardingToken(
            telegram_chat_id=telegram_chat_id,
            token=link_token,
            used=False,
            expires_at=now + timedelta(minutes=_ONBOARDING_TTL_MINUTES),
        )
        self._session.add(onboarding)

        # Persist the OAuth session (CSRF guard)
        # Embed link_token in redirect_to so callback can retrieve it
        oauth_session = OAuthSession(
            state=csrf_state,
            user_id=None,
            redirect_to=link_token,        # re-used as opaque pointer
            expires_at=now + timedelta(minutes=_OAUTH_SESSION_TTL_MINUTES),
        )
        self._session.add(oauth_session)
        await self._session.flush()

        google_url = _build_google_auth_url(
            client_id=self._settings.google_client_id,
            redirect_uri=_callback_uri(self._settings.frontend_url),
            state=csrf_state,
        )
        return BeginLoginResult(google_url=google_url, link_token=link_token)

    # ------------------------------------------------------------------
    # Step 2: Browser returns to /api/auth/callback
    # ------------------------------------------------------------------

    async def handle_callback(self, code: str, state: str) -> CallbackResult:
        """Exchange OAuth code, upsert user, bind Telegram chat.

        Raises :exc:`AuthError` for any recoverable error (expired state,
        bad token, Google API failure, etc.).
        """
        # 1. Validate CSRF state
        oauth_session = await self._get_valid_oauth_session(state)

        # 2. Exchange code for tokens
        token_data = await _exchange_code(
            code=code,
            client_id=self._settings.google_client_id,
            client_secret=self._settings.google_client_secret,
            redirect_uri=_callback_uri(self._settings.frontend_url),
        )

        # 3. Decode the ID token (we trust Google's HTTPS response; no sig verify needed here)
        google_info = _decode_id_token_payload(token_data["id_token"])
        google_id: str = google_info["sub"]
        email: str = google_info["email"]

        # 4. Upsert user
        user = await self._upsert_user(google_id, email, google_info)

        # 5. Bind Telegram if we have an onboarding token
        telegram_chat_id: int | None = None
        link_token: str | None = oauth_session.redirect_to
        if link_token:
            telegram_chat_id = await self._bind_telegram(user, link_token)

        # 6. Mark oauth_session as used (prevent replay)
        await self._session.delete(oauth_session)
        await self._session.flush()

        return CallbackResult(user=user, telegram_chat_id=telegram_chat_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get_valid_oauth_session(self, state: str) -> OAuthSession:
        result = await self._session.execute(
            select(OAuthSession).where(OAuthSession.state == state)
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise AuthError("Invalid or unknown OAuth state")
        now = datetime.now(tz=timezone.utc)
        if session.expires_at.replace(tzinfo=timezone.utc) < now:
            await self._session.delete(session)
            raise AuthError("OAuth state has expired — please restart the login flow")
        return session

    async def _upsert_user(
        self, google_id: str, email: str, google_info: dict[str, object]
    ) -> User:
        """Find by google_id, then by email; create if neither exists."""
        user = await self._repo.find_by_google_id(google_id)
        if user is not None:
            return user

        # Existing account with same email (e.g. registered via a different method)
        user = await self._repo.find_by_email(email)
        if user is not None:
            # Attach the Google identity to the existing account
            user.google_id = google_id
            user.email_verified = bool(google_info.get("email_verified", False))
            user.full_name = user.full_name or str(google_info.get("name", ""))
            user.avatar_url = user.avatar_url or str(google_info.get("picture", ""))
            await self._session.flush()
            await self._session.refresh(user)
            return user

        # Brand-new user
        return await self._repo.create(
            CreateUserData(
                email=email,
                google_id=google_id,
                full_name=str(google_info.get("name", "")) or None,
                avatar_url=str(google_info.get("picture", "")) or None,
                email_verified=bool(google_info.get("email_verified", False)),
            )
        )

    async def _bind_telegram(self, user: User, link_token: str) -> int | None:
        """Consume the onboarding token and link the Telegram chat to the user.

        Returns the chat_id on success, None if the token is invalid/expired/used.
        """
        result = await self._session.execute(
            select(TelegramOnboardingToken).where(
                TelegramOnboardingToken.token == link_token,
                TelegramOnboardingToken.used.is_(False),
            )
        )
        token_row = result.scalar_one_or_none()
        if token_row is None:
            return None

        now = datetime.now(tz=timezone.utc)
        if token_row.expires_at.replace(tzinfo=timezone.utc) < now:
            return None

        chat_id = token_row.telegram_chat_id
        if chat_id is None:
            return None

        # Mark token as used
        token_row.used = True
        token_row.user_id = user.id
        await self._session.flush()

        # Link user ↔ Telegram
        await self._repo.update_telegram_link(
            user.id,
            TelegramLinkData(telegram_chat_id=chat_id),
        )
        return chat_id


# ---------------------------------------------------------------------------
# Pure helpers (no DB, no network)
# ---------------------------------------------------------------------------

def _callback_uri(frontend_url: str) -> str:
    """The OAuth redirect_uri must match what is registered in Google Console."""
    base = frontend_url.rstrip("/")
    return f"{base}/auth/callback"


def _build_google_auth_url(client_id: str, redirect_uri: str, state: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    return f"{_GOOGLE_AUTH_URL}?{urlencode(params)}"


async def _exchange_code(
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict[str, str]:
    """POST to Google token endpoint; return the JSON response.

    Raises :exc:`AuthError` on HTTP or API-level errors.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            _GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
    if resp.status_code != 200:
        raise AuthError(f"Google token exchange failed: {resp.status_code}")
    data = resp.json()
    if "id_token" not in data:
        raise AuthError("Google response missing id_token")
    return data  # type: ignore[return-value]


def _decode_id_token_payload(id_token: str) -> dict[str, object]:
    """Extract claims from the JWT payload without signature verification.

    We skip sig verification because the token was obtained directly from
    Google's token endpoint over HTTPS — MITM is not a practical threat here.
    Production hardening (e.g. google-auth library) is deferred to Sprint 1.
    """
    try:
        parts = id_token.split(".")
        if len(parts) != 3:
            raise AuthError("Malformed id_token")
        # Add padding so base64 decoding doesn't fail
        payload_b64 = parts[1] + "=="
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes)  # type: ignore[return-value]
    except (ValueError, KeyError) as exc:
        raise AuthError(f"Failed to decode id_token: {exc}") from exc
