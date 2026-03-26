# Implementation Plan: StockPulse VN — P0 (Must Have Before Launch)

## Tổng Quan Requirements

6 tính năng P0 bắt buộc phải hoàn thành trước launch:

| # | Tính năng | Điểm | Effort |
|---|-----------|------|--------|
| 1 | Database Schema cơ bản | 7.5 | 3 |
| 2 | Google OAuth Login | 8.0 | 3 |
| 3 | Analytics & Event Tracking | 8.5 | 2 |
| 4 | Telegram Bot – Onboarding (/start) | 9.5 | 3 |
| 5 | Thiết lập Watchlist qua Bot | 9.2 | 3 |
| 6 | Bản tin buổi sáng tự động (8:00) | 9.8 | 4 |

**Mục tiêu đo lường sau P0:** Bot hoạt động ổn định, gửi được bản tin cho 10 beta users, open rate > 50%, có thể track `newsletter_opened`.

---

## Tech Stack (Đề xuất cuối)

| Layer | Technology | Lý do |
|-------|-----------|-------|
| **Backend** | Python + FastAPI | APScheduler tích hợp tốt cho scheduler; ecosystem ML tốt cho AI sau này |
| **Telegram Bot** | python-telegram-bot v20 (async) | Mature, async, phổ biến nhất |
| **Database** | PostgreSQL (Supabase) | Free tier, Auth built-in, real-time subscriptions |
| **Cache** | Redis (Upstash) | Free tier, dùng cho rate limiting & data cache |
| **Scheduler** | APScheduler + Celery | APScheduler cho cron; Celery cho queue gửi bulk |
| **Auth** | Supabase Auth + Google OAuth | Tích hợp sẵn, không cần tự code |
| **Analytics** | PostHog (self-host hoặc cloud) | Free, support custom events, open-source |
| **Data VN** | FireAnt API / VNDirect API | Ưu tiên API chính thức |
| **Data quốc tế** | Yahoo Finance (yfinance) | Miễn phí, đủ cho MVP |
| **Frontend** | Next.js 14 + TailwindCSS | Chỉ cần cho web auth callback ban đầu |
| **Hosting** | Railway / Render | Free tier đủ cho beta |

---

## Sprint 0 — Foundation (Tuần 1–2)

### Task 0.1: Project Setup & Infrastructure

- [ ] Tạo monorepo structure:
  ```
  stockpulse-vn/
  ├── backend/          # FastAPI + Bot
  ├── frontend/         # Next.js (minimal)
  ├── infra/            # Docker, env templates
  └── docs/
  ```
- [ ] Setup Docker Compose (PostgreSQL + Redis local)
- [ ] Setup Supabase project (staging + production)
- [ ] Setup environment variables template (`.env.example`)
- [ ] Setup CI/CD cơ bản (GitHub Actions: lint + test)

### Task 0.2: Database Schema

Tables cần tạo:

```sql
-- users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  google_id VARCHAR UNIQUE NOT NULL,
  email VARCHAR UNIQUE NOT NULL,
  display_name VARCHAR,
  avatar_url VARCHAR,
  telegram_chat_id BIGINT UNIQUE,
  telegram_linked_at TIMESTAMPTZ,
  subscription_tier VARCHAR DEFAULT 'free', -- free | pro | premium
  subscription_expires_at TIMESTAMPTZ,
  notification_hour INTEGER DEFAULT 8, -- preferred hour
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- watchlists
CREATE TABLE watchlists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  ticker VARCHAR(10) NOT NULL,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, ticker)
);

-- notification_logs
CREATE TABLE notification_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR NOT NULL, -- morning_newsletter | evening_newsletter | price_alert | rsi_alert
  telegram_message_id INTEGER,
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  opened_at TIMESTAMPTZ, -- tracked via inline button click
  status VARCHAR DEFAULT 'sent' -- sent | delivered | failed | opened
);

-- telegram_link_tokens (OTP để link Google ↔ Telegram)
CREATE TABLE telegram_link_tokens (
  token VARCHAR(64) PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  telegram_chat_id BIGINT,
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ
);
```

- [ ] Viết migrations với Alembic
- [ ] Tạo indexes: `watchlists(user_id)`, `notification_logs(user_id, sent_at)`, `users(telegram_chat_id)`
- [ ] Viết unit tests cho schema constraints

### Task 0.3: Google OAuth

- [ ] Setup Supabase Auth với Google provider
- [ ] Tạo Next.js minimal app (chỉ cần `/auth/callback` route)
- [ ] Flow:
  1. Telegram bot gửi link: `https://app.stockpulse.vn/auth/google?token=<link_token>`
  2. User đăng nhập Google → callback tạo/update record trong `users`
  3. Lưu `telegram_chat_id` vào user record
  4. Bot nhận webhook xác nhận liên kết thành công
- [ ] Viết integration tests cho OAuth flow

### Task 0.4: Analytics & Event Tracking

Setup PostHog, implement 21 events từ ngày 1:

**Critical events (implement trong P0):**

| Event | Trigger | Properties |
|-------|---------|-----------|
| `bot_started` | User gửi /start | `telegram_chat_id` |
| `onboarding_completed` | User link Google thành công | `user_id`, `time_to_complete` |
| `watchlist_ticker_added` | User thêm mã | `user_id`, `ticker`, `watchlist_size` |
| `watchlist_ticker_removed` | User xóa mã | `user_id`, `ticker` |
| `newsletter_sent` | Bot gửi bản tin | `user_id`, `newsletter_type` |
| `newsletter_opened` | User nhấn nút trong bản tin | `user_id`, `newsletter_type`, `time_to_open` |
| `bot_blocked` | User block bot | `user_id` |
| `auth_google_started` | User click link đăng nhập | `telegram_chat_id` |
| `auth_google_completed` | OAuth callback thành công | `user_id` |

- [ ] Setup PostHog SDK trong FastAPI
- [ ] Tạo `analytics.py` service wrapper
- [ ] Viết tests để verify events được fire đúng

---

## Sprint 1 — Core Loop (Tuần 3–5)

### Task 1.1: Telegram Bot – Onboarding

Commands cần implement:

| Command | Chức năng |
|---------|----------|
| `/start` | Chào mừng + hướng dẫn 3 bước setup |
| `/login` | Gửi link đăng nhập Google |
| `/status` | Hiện trạng thái tài khoản (linked/unlinked, tier) |
| `/help` | Danh sách commands |

**Onboarding flow:**
```
1. User gửi /start
2. Bot hiện tin nhắn chào + nút "Đăng nhập với Google"
3. User click → redirect OAuth → link thành công
4. Bot gửi tin: "✅ Đã liên kết! Dùng /watch để thêm cổ phiếu"
5. User thêm mã → Bot xác nhận
6. Bot hướng dẫn: "Bạn sẽ nhận bản tin lúc 8:00 sáng mỗi ngày"
→ onboarding_completed event
```

- [ ] Implement bot handlers với python-telegram-bot v20
- [ ] Implement inline keyboards cho onboarding steps
- [ ] Xử lý edge cases: user block bot, link token expired, duplicate link attempt
- [ ] Viết unit tests cho mỗi command handler

### Task 1.2: Watchlist Management qua Bot

| Command | Chức năng |
|---------|----------|
| `/watch VCB` | Thêm VCB vào watchlist |
| `/unwatch VCB` | Xóa VCB khỏi watchlist |
| `/watchlist` | Hiện danh sách mã đang theo dõi |

**Business rules:**
- Free: tối đa 3 mã
- Pro: tối đa 10 mã
- Validate ticker hợp lệ (gọi API check ticker exists)
- Nếu đạt giới hạn Free: hiện thông báo upgrade

- [ ] Implement CRUD watchlist handlers
- [ ] Validate ticker via VNDirect/FireAnt API
- [ ] Implement upgrade prompt khi đạt giới hạn
- [ ] Viết unit tests + integration tests

### Task 1.3: Data Integration — VN Market Data

- [ ] Tích hợp VNDirect API (hoặc FireAnt API nếu có key):
  - VN-Index, HNX-Index, UPCOM: điểm, % thay đổi, KLGD
  - Top 5 tăng mạnh nhất / giảm mạnh nhất
  - Giá đóng cửa + KLGD cho từng mã trong watchlist
- [ ] Implement Redis caching (TTL: 5 phút trong giờ giao dịch)
- [ ] Implement fallback nếu API down (dùng cached data + thông báo)
- [ ] Rate limiting để tránh bị ban API
- [ ] Viết integration tests với mock API responses

### Task 1.4: Bản Tin Buổi Sáng (8:00)

**Cấu trúc bản tin:**

```
📊 BẢN TIN SÁNG | Thứ Ba, 25/03/2026

🇻🇳 THỊ TRƯỜNG VN
VN-Index: 1,285.4 (+0.8%) | KLGD: 18,450 tỷ
HNX:      245.2 (+0.3%)
UPCOM:    95.8  (-0.1%)

🏆 TOP 5 TĂNG MẠNH
1. MSN  +6.8% | 2. VHM +5.2% | ...

📉 TOP 5 GIẢM MẠNH
1. HPG  -3.1% | 2. GAS -2.8% | ...

📌 WATCHLIST CỦA BẠN
• VCB: 88,500 (+1.2%) | KL: 2.1M
• VHM: 45,200 (+5.2%) | KL: 8.5M ⚡ Đột biến KL
• FPT: 152,000 (-0.5%)

📅 SỰ KIỆN HÔM NAY
• VCB: Ngày GD không hưởng cổ tức (500đ/cp)

[📖 Xem chi tiết] [⚙️ Cài đặt]
```

- [ ] Implement APScheduler cron job (8:00 AM Vietnam time GMT+7)
- [ ] Implement message builder service
- [ ] Bulk send cho tất cả active users (dùng Celery)
- [ ] Xử lý `TelegramError` (user block bot → update `is_active=false`)
- [ ] Track `newsletter_sent` và add inline button để track `newsletter_opened`
- [ ] Viết unit tests cho message builder
- [ ] Viết integration tests cho scheduler

---

## Rủi Ro & Mitigation

| Rủi ro | Mức độ | Mitigation |
|--------|--------|-----------|
| VNDirect/FireAnt API không ổn định hoặc thay đổi | CAO | Implement circuit breaker; cache 15 phút; fallback message nếu data không available |
| Telegram rate limiting (30 msg/giây) | CAO | Celery queue với rate limiting; batch send với delay |
| Google OAuth callback URL thay đổi môi trường | TRUNG BÌNH | Config-driven callback URL; test cả staging và prod |
| PostgreSQL connection pool exhaustion khi bulk send | TRUNG BÌNH | Connection pooling với PgBouncer; async SQLAlchemy |
| User data privacy (PDPA) | CAO | Không lưu dữ liệu tài chính user; encrypt `telegram_chat_id`; thêm disclaimer trong /start |
| Ticker validation — mã không tồn tại | THẤP | Whitelist từ API; fuzzy match để suggest mã gần đúng |

---

## Định Nghĩa Done (DoD)

P0 hoàn thành khi:
- [ ] 10 beta users có thể onboard end-to-end (Telegram → Google Auth → Watchlist → nhận bản tin)
- [ ] Bản tin 8:00 sáng gửi đúng giờ, không lỗi, trong 3 ngày liên tiếp
- [ ] Analytics dashboard hiện được `newsletter_opened` rate
- [ ] Tất cả P0 tasks có unit tests, coverage ≥ 80%
- [ ] Không có security issues (no hardcoded secrets, input validated)

---

## Estimated Complexity: HIGH

- Sprint 0 (Tuần 1–2): Infrastructure + Schema + OAuth + Analytics
- Sprint 1 (Tuần 3–5): Bot + Watchlist + Data Integration + Newsletter
