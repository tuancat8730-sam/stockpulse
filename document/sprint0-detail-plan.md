# Sprint 0 — Foundation (Tuần 1–2)

**Goal:** Database schema | Google OAuth | Telegram Bot /start | Analytics | Bot hoạt động ổn

**Definition of Done:**
- [ ] Bot nhận `/start` và trả lời welcome message
- [ ] Bot gửi OAuth link, user login Google thành công
- [ ] Bot nhận confirmation "đã liên kết"
- [ ] 3 analytics events (`bot_started`, `auth_google_started`, `auth_google_completed`) xuất hiện trong PostHog
- [ ] Unit test coverage ≥ 80% cho code đã viết
- [ ] Staging deploy hoạt động

---

## Phase 0.1 — Project Scaffolding (Day 1–2) ✅ DONE

| Task ID | Task | File / Output | Effort | Depends on | Status |
|---------|------|---------------|--------|------------|--------|
| 0.1.1 | Tạo monorepo structure + `pyproject.toml` (fastapi, uvicorn, python-telegram-bot, sqlalchemy, asyncpg, alembic, redis, apscheduler, posthog, httpx, pydantic-settings, pytest) | `backend/pyproject.toml` | 0.25d | — | ✅ Done |
| 0.1.2 | Pydantic Settings — validate tất cả env vars khi startup | `backend/app/config.py` | 0.25d | 0.1.1 | ✅ Done |
| 0.1.3 | Docker Compose local dev (PostgreSQL 16 + Redis 7, healthchecks, volumes) | `infra/docker-compose.yml` | 0.25d | — | ✅ Done |
| 0.1.4 | Next.js 14 minimal app — chỉ `/auth/google` + `/auth/callback` routes | `frontend/` | 0.25d | — | ✅ Done |
| 0.1.5 | GitHub Actions CI (ruff lint + mypy + pytest) | `.github/workflows/ci.yml` | 0.25d | 0.1.1 | ✅ Done |
| 0.1.6 | `.env.example` với tất cả required secrets | `infra/.env.example` | 0.1d | 0.1.2 | ✅ Done |

### Kết quả Task 0.1.1 (2026-03-26)

**Commit:** `f890975` — `feat: task 0.1.1 — monorepo scaffolding, pyproject.toml, CI, Docker`

**Files đã tạo:**

| File | Nội dung |
|------|----------|
| `backend/pyproject.toml` | 14 runtime deps + ruff/mypy/pytest, Python 3.12, coverage ≥80% |
| `backend/app/config.py` | Pydantic Settings, validate APP_SECRET_KEY ≥32 chars, auto-fix asyncpg URL |
| `infra/docker-compose.yml` | PostgreSQL 16 (port 5433) + Redis 7 (port 6380), healthchecks, volumes |
| `infra/.env.example` | 14 secrets documented với hướng dẫn |
| `frontend/package.json` | Next.js 14.2.29 + TypeScript + Tailwind |
| `frontend/src/app/auth/callback/page.tsx` | OAuth callback: loading/success/error states, deeplink Telegram |
| `frontend/src/app/layout.tsx` | Root layout |
| `frontend/src/app/page.tsx` | Landing page placeholder |
| `.github/workflows/ci.yml` | CI: ruff + mypy + pytest (Python) với Postgres/Redis services; lint + build (Next.js) |
| `.gitignore` | Exclude .env, node_modules, __pycache__, .venv |
| `README.md` | Quick start guide |
| `backend/app/` | Package structure: models/, repositories/, services/, routers/, bot/handlers/, core/, jobs/ |

**Ghi chú thực tế:**
- Dùng `python-telegram-bot>=21.0` (không phải v20 như plan, v21 là stable mới nhất)
- PostgreSQL port 5433 (tránh conflict với host PostgreSQL mặc định 5432)
- Redis port 6380 (tránh conflict với host Redis mặc định 6379)
- `config.py` tự động convert `postgresql://` → `postgresql+asyncpg://` để đảm bảo async driver

**Required secrets (`.env.example`):**
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `TELEGRAM_BOT_TOKEN`
- `REDIS_URL` (Upstash)
- `POSTHOG_API_KEY`, `POSTHOG_HOST`
- `DATABASE_URL`
- `APP_SECRET_KEY`
- `FRONTEND_URL`

---

## Phase 0.2 — Database Setup (Day 2–3)

| Task ID | Task | File / Output | Effort | Depends on |
|---------|------|---------------|--------|------------|
| 0.2.1 | Async SQLAlchemy engine + session factory (pool_size=5) | `backend/app/core/database.py` | 0.25d | 0.1.2 |
| 0.2.2 | ORM Models cho P0 tables: `users`, `telegram_onboarding_tokens` (**user_id nullable** + `telegram_chat_id` column), `watchlist_items`, `notification_logs`, `stock_tickers`, `analytics_events` | `backend/app/models/` | 0.5d | 0.2.1 |
| 0.2.3 | Alembic migrations — 6 files theo sprint scope (không tạo P3/P4 tables): `001_auth_users`, `002_subscriptions`, `003_watchlist`, `004_newsletter`, `005_market_data`, `006_analytics` | `backend/alembic/versions/` | 0.5d | 0.2.2 |
| 0.2.4 | Seed data: `subscription_plans` (free/pro/premium) + `stock_tickers` từ HOSE/HNX/UPCOM CSV | `backend/alembic/versions/002` | 0.25d | 0.2.3 |
| 0.2.5 | `UserRepository`: `find_by_google_id`, `find_by_telegram_chat_id`, `create`, `update_telegram_link` — tất cả return new objects (immutable) | `backend/app/repositories/user_repo.py` | 0.25d | 0.2.2 |
| 0.2.6 | Unit tests: schema constraints (unique, check), repository CRUD với test DB | `backend/tests/unit/test_user_repo.py` | 0.25d | 0.2.5 |

**Lưu ý schema critical:** `telegram_onboarding_tokens.user_id` PHẢI là nullable vì user chưa tồn tại khi /start được gọi lần đầu.

---

## Phase 0.3 — Google OAuth (Day 3–4.5)

| Task ID | Task | File / Output | Effort | Depends on |
|---------|------|---------------|--------|------------|
| 0.3.1 | `AuthService`: generate CSRF state → store trong `oauth_sessions`, build Google OAuth URL, exchange code cho tokens via `httpx`, extract user info từ ID token, create/update `users`, bind `telegram_chat_id` từ `link_token` | `backend/app/services/auth_service.py` | 0.5d | 0.2.5 |
| 0.3.2 | FastAPI auth routes: `GET /api/auth/google?token=<link_token>` (redirect to Google) + `GET /api/auth/callback` (exchange code, link Telegram, redirect to success page) | `backend/app/routers/auth.py` | 0.25d | 0.3.1 |
| 0.3.3 | Next.js callback page: hiển thị "Đã liên kết thành công! Quay lại Telegram" + deeplink `tg://resolve?domain=<bot_username>` | `frontend/app/auth/callback/page.tsx` | 0.25d | 0.3.2 |
| 0.3.4 | Integration tests OAuth flow: new user creation, existing user update, token linking, expired token rejection, duplicate link attempt | `backend/tests/integration/test_auth_flow.py` | 0.25d | 0.3.1, 0.3.2 |

---

## Phase 0.4 — Analytics (Day 4.5–5.5)

| Task ID | Task | File / Output | Effort | Depends on |
|---------|------|---------------|--------|------------|
| 0.4.1 | `AnalyticsService` wrapper PostHog Python SDK — non-blocking (background thread), ghi song song vào `analytics_events` table | `backend/app/services/analytics_service.py` | 0.25d | 0.2.2, 0.1.2 |
| 0.4.2 | P0 event constants (9 events): `bot_started`, `onboarding_completed`, `watchlist_ticker_added`, `watchlist_ticker_removed`, `newsletter_sent`, `newsletter_opened`, `bot_blocked`, `auth_google_started`, `auth_google_completed` | `backend/app/services/analytics_events.py` | 0.1d | — |
| 0.4.3 | Unit tests: verify events fire với đúng properties, mock PostHog client, verify DB write | `backend/tests/unit/test_analytics_service.py` | 0.25d | 0.4.1 |

---

## Phase 0.5 — FastAPI Bootstrap + Telegram Bot /start (Day 5.5–7)

| Task ID | Task | File / Output | Effort | Depends on |
|---------|------|---------------|--------|------------|
| 0.5.1 | FastAPI main app với lifespan: init DB engine, connect Redis, đăng ký bot webhook, start APScheduler. Shutdown: close all connections | `backend/app/main.py` | 0.25d | 0.2.1, 0.3.2 |
| 0.5.2 | Health check endpoint: `GET /api/health` → DB status + Redis status + bot webhook status | `backend/app/routers/health.py` | 0.1d | 0.5.1 |
| 0.5.3 | Telegram Bot setup: python-telegram-bot v20 Application, webhook mode tại `/webhook/tg` (không dùng polling), đăng ký command handlers | `backend/app/bot/setup.py` | 0.25d | 0.5.1 |
| 0.5.4 | `/start` handler: check linked/unlinked → welcome message + inline keyboard "Đăng nhập với Google" → fire `bot_started` event | `backend/app/bot/handlers/start.py` | 0.25d | 0.5.3, 0.4.1 |
| 0.5.5 | `/login` handler: tạo `telegram_onboarding_token` (user_id=NULL, telegram_chat_id stored, TTL 10 phút) → gửi OAuth link → fire `auth_google_started` | `backend/app/bot/handlers/login.py` | 0.25d | 0.5.3, 0.3.1 |
| 0.5.6 | Link completion callback: sau OAuth thành công, `AuthService` gọi `bot.send_message(chat_id, "Liên kết thành công!")` → fire `auth_google_completed` | `backend/app/services/auth_service.py` (update) | 0.25d | 0.5.4, 0.3.1 |
| 0.5.7 | Vietnamese message templates cho /start và link flows | `backend/app/bot/messages.py` | 0.1d | — |
| 0.5.8 | Unit tests: /start handler (new user / returning user), /login flow, expired token, analytics events fired | `backend/tests/unit/test_bot_handlers.py` | 0.25d | 0.5.4, 0.5.5 |

**Scope /start trong Sprint 0 (KHÔNG làm thêm):**
- ✅ Welcome message + inline keyboard "Đăng nhập với Google"
- ✅ Gửi OAuth link qua /login
- ✅ Nhận notification link thành công
- ✅ Fire analytics events
- ❌ KHÔNG: `/help`, `/status`, edge cases phức tạp, full onboarding 6 bước → Sprint 1

---

## Phase 0.6 — E2E Verification (Day 7)

| Task ID | Task | File / Output | Effort | Depends on |
|---------|------|---------------|--------|------------|
| 0.6.1 | Smoke test e2e: `/start` → click OAuth link → Google login → bot nhận confirmation message | `backend/tests/integration/test_e2e_onboarding.py` | 0.25d | 0.5.6 |
| 0.6.2 | Verify analytics pipeline: `bot_started` + `auth_google_started` + `auth_google_completed` xuất hiện trong PostHog dashboard | Manual checklist | 0.1d | 0.6.1 |
| 0.6.3 | Deploy staging lên Railway (backend) + Vercel (frontend), test thật với Telegram bot | Staging environment | 0.25d | 0.5.1, 0.3.3 |

---

## Tổng hợp

| Phase | Ngày | Effort | Deliverable chính | Status |
|-------|------|--------|-------------------|--------|
| 0.1 Project Scaffolding | 1–2 | 1.3d | Monorepo, Docker, CI | ✅ Done |
| 0.2 Database | 2–3 | 2.0d | Schema, migrations, UserRepo | ⏳ Next |
| 0.3 Google OAuth | 3–4.5 | 1.25d | OAuth flow end-to-end | 🔲 Pending |
| 0.4 Analytics | 4.5–5.5 | 0.6d | PostHog + 9 events | 🔲 Pending |
| 0.5 FastAPI + Bot /start | 5.5–7 | 1.7d | Bot hoạt động, link flow | 🔲 Pending |
| 0.6 E2E Verification | 7 | 0.6d | "Bot hoạt động ổn" confirmed | 🔲 Pending |
| **Total** | **7 ngày** | **~7.5d** | **Sprint 0 Done** | **1/6 phases** |

---

## Critical Path

```
0.1.1 Monorepo
  │
  ├─► 0.1.2 Config ─► 0.2.1 DB Engine ─► 0.2.2 ORM Models ─► 0.2.3 Migrations
  │                                                                │
  │                                                           0.2.5 UserRepo
  │                                                                │
  │                                              ┌────────────────┘
  │                                              │
  │                                         0.3.1 AuthService ─► 0.3.2 Routes
  │                                              │
  │                              ┌───────────────┘
  │                              │
  │                         0.5.1 FastAPI App ─► 0.5.3 Bot Setup ─► 0.5.4 /start
  │                              │                                        │
  │                         0.4.1 Analytics ◄────────────────────────────┘
  │
  └─► 0.6.1 E2E Smoke Test ─► 0.6.3 Staging Deploy
```

**Longest chain:** Monorepo → Config → DB Engine → ORM → Migrations → UserRepo → AuthService → FastAPI → Bot → /start → E2E Test

---

## Rủi ro Sprint 0

| Rủi ro | Mức độ | Mitigation |
|--------|--------|-----------|
| `telegram_onboarding_tokens.user_id NOT NULL` trong schema gốc | CAO | Fix ngay tại 0.2.2/0.2.3: make nullable, add `telegram_chat_id` column |
| Google OAuth callback URL mismatch giữa local/staging/prod | TRUNG BÌNH | Config-driven `FRONTEND_URL`, đăng ký cả localhost và production URL trong Google Console |
| Railway free tier ngủ sau 15 phút (giết APScheduler) | TRUNG BÌNH | Dùng cron-job.org (free) ping health endpoint lúc 7:50 AM để wake trước newsletter |
| python-telegram-bot v20 webhook mode tích hợp với FastAPI | TRUNG BÌNH | Webhook mode: FastAPI nhận POST tại `/webhook/tg`, forward cho bot Application |
| Supabase free tier max 2 direct connections | THẤP | pool_size=5 + Supabase connection pooler (pgbouncer, 50 connections free) |
