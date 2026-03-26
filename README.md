# StockPulse VN

Bản tin chứng khoán Việt Nam cá nhân hóa qua Telegram.

## Cấu trúc

```
stockpulse-vn/
├── backend/          # Python + FastAPI + Telegram Bot
├── frontend/         # Next.js 14 (auth callback)
├── infra/            # Docker Compose, env templates
├── document/         # Planning docs, schema
└── .github/          # CI/CD workflows
```

## Quick Start (Local Dev)

```bash
# 1. Start PostgreSQL + Redis
docker compose -f infra/docker-compose.yml up -d

# 2. Setup backend
cd backend
cp ../infra/.env.example .env  # fill in real values
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# 3. Setup frontend
cd frontend
npm install
npm run dev
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + FastAPI |
| Bot | python-telegram-bot v21 |
| Database | PostgreSQL 16 (Supabase) |
| Cache | Redis 7 (Upstash) |
| Scheduler | APScheduler |
| Auth | Google OAuth via Supabase |
| Analytics | PostHog |
| Frontend | Next.js 14 + Tailwind |
