"""Auth router — Google OAuth 2.0 endpoints.

Routes:
  GET /api/auth/google?chat_id=<int>
      → 302 redirect to Google consent page
      → Query param `chat_id` identifies the Telegram user initiating login.

  GET /api/auth/callback?code=<str>&state=<str>
      → Exchange code, upsert user, bind Telegram, redirect to frontend
      → On success: redirects to {FRONTEND_URL}/auth/callback?linked=1
      → On failure: redirects to {FRONTEND_URL}/auth/callback?error=<reason>
"""

from __future__ import annotations

import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.database import get_db_session
from app.services.auth_service import AuthError, AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

def _get_auth_service(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_db_session),
) -> AuthService:
    return AuthService(settings=settings, session=session)


# ---------------------------------------------------------------------------
# GET /api/auth/google
# ---------------------------------------------------------------------------

@router.get("/google", response_class=RedirectResponse, status_code=302)
async def start_google_oauth(
    chat_id: int = Query(..., description="Telegram chat_id of the user initiating login"),
    service: AuthService = Depends(_get_auth_service),
) -> RedirectResponse:
    """Initiate Google OAuth flow.

    Creates a TelegramOnboardingToken and OAuthSession in the DB, then
    redirects the browser to Google's consent page.
    """
    try:
        result = await service.begin_login(telegram_chat_id=chat_id)
        return RedirectResponse(url=result.google_url, status_code=302)
    except Exception:
        logger.exception("Failed to begin OAuth login for chat_id=%s", chat_id)
        raise


# ---------------------------------------------------------------------------
# GET /api/auth/callback
# ---------------------------------------------------------------------------

@router.get("/callback", response_class=RedirectResponse, status_code=302)
async def google_oauth_callback(
    settings: Settings = Depends(get_settings),
    service: AuthService = Depends(_get_auth_service),
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="CSRF state parameter"),
    error: str | None = Query(None, description="OAuth error from Google (user denied, etc.)"),
) -> RedirectResponse:
    """Handle Google's redirect after user consents (or denies).

    On success: redirects to {FRONTEND_URL}/auth/callback?linked=1&email=…
    On failure: redirects to {FRONTEND_URL}/auth/callback?error=<reason>
    """
    base = settings.frontend_url.rstrip("/") + "/auth/callback"

    # User denied consent in Google dialog
    if error:
        logger.info("OAuth denied by user: %s", error)
        return RedirectResponse(
            url=f"{base}?{urlencode({'error': error})}",
            status_code=302,
        )

    try:
        result = await service.handle_callback(code=code, state=state)
        params: dict[str, str | int] = {"linked": "1", "email": result.user.email}
        if result.telegram_chat_id is not None:
            params["chat_id"] = result.telegram_chat_id
        return RedirectResponse(url=f"{base}?{urlencode(params)}", status_code=302)

    except AuthError as exc:
        logger.warning("AuthError during callback: %s", exc)
        return RedirectResponse(
            url=f"{base}?{urlencode({'error': str(exc)})}",
            status_code=302,
        )
    except Exception:
        logger.exception("Unexpected error during OAuth callback")
        return RedirectResponse(
            url=f"{base}?{urlencode({'error': 'internal_error'})}",
            status_code=302,
        )
