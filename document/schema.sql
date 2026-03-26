-- =============================================================================
-- StockPulse VN — Production PostgreSQL Schema
-- =============================================================================
-- DISCLAIMER: This platform provides market data and news analysis for
-- informational purposes only. Nothing herein constitutes financial advice.
-- Users must consult licensed financial advisors before making investment
-- decisions. StockPulse VN bears no liability for investment outcomes.
-- =============================================================================
--
-- Domain Overview:
--   1. Auth & Users            — Google OAuth, Telegram binding, soft deletes
--   2. Subscriptions & Payments — Plans, PayOS transactions, billing history
--   3. Watchlist & Alerts      — Ticker watchlists, price/RSI/volume alerts
--   4. Newsletter & Notifications — Campaigns, sends, open tracking
--   5. Market Data             — Tickers, EOD prices, technicals, foreign flow,
--                                 corporate events, news, global indicators
--   6. Blog & Content          — Admin CMS: draft/review/publish/archive
--   7. Community & Moderation  — User posts, likes, comments, reports, badges
--   8. Analytics               — Event stream (21 tracked events)
--   9. Referral & NPS          — Referral program, NPS surveys
--
-- Conventions:
--   • Primary keys  : UUID gen_random_uuid()
--   • Timestamps    : TIMESTAMPTZ (UTC stored; app converts to UTC+7 for display)
--   • Monetary VND  : NUMERIC(15,2)
--   • Stock prices  : NUMERIC(12,2)
--   • Enum fields   : VARCHAR + CHECK constraint (no native ENUM for easy migrations)
--   • Soft deletes  : deleted_at TIMESTAMPTZ NULL
--   • FK indexes    : every FK column has a dedicated index
--   • Real-time data: in Redis cache — NOT in this schema
--   • PDPA note     : no sensitive financial data (bank accounts, balances) stored
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Utility: auto-update updated_at trigger function
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Helper macro: attach updated_at trigger to a table
-- Usage: SELECT attach_updated_at_trigger('table_name');
CREATE OR REPLACE FUNCTION attach_updated_at_trigger(p_table TEXT)
RETURNS VOID AS $$
BEGIN
  EXECUTE format(
    'CREATE TRIGGER trg_%I_updated_at
     BEFORE UPDATE ON %I
     FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at()',
    p_table, p_table
  );
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 1. AUTH & USERS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- users
-- Core identity table. Google OAuth is the primary auth method.
-- Telegram is linked separately. Soft-deleted via deleted_at.
-- ---------------------------------------------------------------------------
CREATE TABLE users (
  id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Google OAuth
  google_id           TEXT        UNIQUE,          -- Google subject ID
  email               TEXT        UNIQUE NOT NULL,
  email_verified      BOOLEAN     NOT NULL DEFAULT FALSE,
  full_name           TEXT,
  avatar_url          TEXT,

  -- Telegram binding (set after /login flow)
  telegram_chat_id    BIGINT      UNIQUE,          -- Telegram chat_id (nullable until linked)
  telegram_username   TEXT,
  telegram_linked_at  TIMESTAMPTZ,

  -- Account state
  status              VARCHAR(20) NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'suspended', 'deactivated')),

  -- Soft delete (PDPA right-to-erasure)
  deleted_at          TIMESTAMPTZ,

  -- Referral
  referral_code       TEXT        UNIQUE NOT NULL DEFAULT substr(md5(gen_random_uuid()::TEXT), 1, 8),
  referred_by_user_id UUID        REFERENCES users (id) ON DELETE SET NULL,

  -- Watchlist slot bonus from referrals (stacks with plan quota)
  bonus_watchlist_slots INT        NOT NULL DEFAULT 0 CHECK (bonus_watchlist_slots >= 0),

  -- NPS
  nps_eligible_at     TIMESTAMPTZ,   -- set to created_at + 30 days on insert
  nps_sent_at         TIMESTAMPTZ,

  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email             ON users (email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_google_id         ON users (google_id) WHERE google_id IS NOT NULL;
CREATE INDEX idx_users_telegram_chat_id  ON users (telegram_chat_id) WHERE telegram_chat_id IS NOT NULL;
CREATE INDEX idx_users_referred_by       ON users (referred_by_user_id) WHERE referred_by_user_id IS NOT NULL;
CREATE INDEX idx_users_referral_code     ON users (referral_code);
CREATE INDEX idx_users_deleted_at        ON users (deleted_at) WHERE deleted_at IS NOT NULL;

SELECT attach_updated_at_trigger('users');

-- ---------------------------------------------------------------------------
-- oauth_sessions
-- Short-lived OAuth state tokens for CSRF protection during Google login flow.
-- ---------------------------------------------------------------------------
CREATE TABLE oauth_sessions (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  state       TEXT        NOT NULL UNIQUE,   -- random CSRF token
  user_id     UUID        REFERENCES users (id) ON DELETE CASCADE,  -- NULL before auth
  redirect_to TEXT,
  expires_at  TIMESTAMPTZ NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_oauth_sessions_state      ON oauth_sessions (state);
CREATE INDEX idx_oauth_sessions_expires_at ON oauth_sessions (expires_at);

-- ---------------------------------------------------------------------------
-- telegram_onboarding_tokens
-- One-time tokens generated by web → sent to Telegram bot for /login linking.
-- ---------------------------------------------------------------------------
CREATE TABLE telegram_onboarding_tokens (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  token       TEXT        NOT NULL UNIQUE,
  used        BOOLEAN     NOT NULL DEFAULT FALSE,
  expires_at  TIMESTAMPTZ NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tg_onboarding_tokens_token   ON telegram_onboarding_tokens (token) WHERE NOT used;
CREATE INDEX idx_tg_onboarding_tokens_user_id ON telegram_onboarding_tokens (user_id);

-- =============================================================================
-- 2. SUBSCRIPTIONS & PAYMENTS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- subscription_plans
-- Seed data: free, pro (99k/mo), premium (299k/mo)
-- ---------------------------------------------------------------------------
CREATE TABLE subscription_plans (
  id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  slug                 VARCHAR(30) NOT NULL UNIQUE,   -- 'free', 'pro', 'premium'
  name                 TEXT        NOT NULL,
  price_vnd            NUMERIC(15,2) NOT NULL DEFAULT 0 CHECK (price_vnd >= 0),
  billing_period_days  INT         NOT NULL DEFAULT 30 CHECK (billing_period_days > 0),
  watchlist_limit      INT         NOT NULL DEFAULT 3 CHECK (watchlist_limit > 0),
                         -- -1 = unlimited (premium)
  alert_limit          INT         NOT NULL DEFAULT 0 CHECK (alert_limit >= 0),
                         -- -1 = unlimited
  features             JSONB       NOT NULL DEFAULT '{}',  -- feature flags
  is_active            BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT attach_updated_at_trigger('subscription_plans');

-- Seed plans (idempotent)
INSERT INTO subscription_plans (slug, name, price_vnd, billing_period_days, watchlist_limit, alert_limit, features)
VALUES
  ('free',    'Free',    0,      30, 3,  0,  '{"morning_newsletter":true,"evening_newsletter":false,"ai_news":false,"price_alerts":false,"rsi_alerts":false,"volume_alerts":false,"technical_analysis":false,"global_indicators":false,"web_dashboard":false}'),
  ('pro',     'Pro',     99000,  30, 10, 10, '{"morning_newsletter":true,"evening_newsletter":true,"ai_news":true,"price_alerts":true,"rsi_alerts":false,"volume_alerts":false,"technical_analysis":false,"global_indicators":false,"web_dashboard":true}'),
  ('premium', 'Premium', 299000, 30, -1, -1, '{"morning_newsletter":true,"evening_newsletter":true,"ai_news":true,"price_alerts":true,"rsi_alerts":true,"volume_alerts":true,"technical_analysis":true,"global_indicators":true,"web_dashboard":true}')
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------------
-- user_subscriptions
-- Active or historical subscription records per user.
-- ---------------------------------------------------------------------------
CREATE TABLE user_subscriptions (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  plan_id          UUID        NOT NULL REFERENCES subscription_plans (id),
  status           VARCHAR(20) NOT NULL DEFAULT 'active'
                     CHECK (status IN ('active', 'cancelled', 'expired', 'past_due', 'trialing')),
  started_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at       TIMESTAMPTZ NOT NULL,
  cancelled_at     TIMESTAMPTZ,
  cancel_reason    TEXT,
  -- Track plan price at time of subscription for billing history
  price_paid_vnd   NUMERIC(15,2) NOT NULL DEFAULT 0,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_subscriptions_user_id   ON user_subscriptions (user_id);
CREATE INDEX idx_user_subscriptions_plan_id   ON user_subscriptions (plan_id);
CREATE INDEX idx_user_subscriptions_status    ON user_subscriptions (status);
CREATE INDEX idx_user_subscriptions_expires_at ON user_subscriptions (expires_at) WHERE status = 'active';

SELECT attach_updated_at_trigger('user_subscriptions');

-- ---------------------------------------------------------------------------
-- payment_transactions
-- PayOS payment records. Do NOT store card/bank credentials here.
-- ---------------------------------------------------------------------------
CREATE TABLE payment_transactions (
  id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID        NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
  subscription_id     UUID        REFERENCES user_subscriptions (id) ON DELETE SET NULL,
  plan_id             UUID        NOT NULL REFERENCES subscription_plans (id),

  -- PayOS fields
  payos_order_id      TEXT        UNIQUE NOT NULL,    -- PayOS orderCode
  payos_payment_link  TEXT,
  payos_transaction_id TEXT,                          -- PayOS transactionId after success

  amount_vnd          NUMERIC(15,2) NOT NULL CHECK (amount_vnd > 0),
  currency            VARCHAR(3)  NOT NULL DEFAULT 'VND',

  status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'paid', 'failed', 'cancelled', 'refunded')),

  paid_at             TIMESTAMPTZ,
  expires_at          TIMESTAMPTZ,                   -- payment link expiry
  webhook_payload     JSONB,                          -- raw PayOS webhook for audit
  failure_reason      TEXT,

  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_tx_user_id       ON payment_transactions (user_id);
CREATE INDEX idx_payment_tx_subscription  ON payment_transactions (subscription_id);
CREATE INDEX idx_payment_tx_payos_order   ON payment_transactions (payos_order_id);
CREATE INDEX idx_payment_tx_status        ON payment_transactions (status);

SELECT attach_updated_at_trigger('payment_transactions');

-- =============================================================================
-- 3. WATCHLIST & ALERTS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- watchlist_items
-- Each row = one ticker in a user's watchlist.
-- Quota enforced at application layer using plan watchlist_limit + bonus slots.
-- ---------------------------------------------------------------------------
CREATE TABLE watchlist_items (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  ticker      VARCHAR(10) NOT NULL,   -- e.g. 'VCB', 'HPG', 'VNM'
  added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sort_order  INT         NOT NULL DEFAULT 0,

  UNIQUE (user_id, ticker)
);

CREATE INDEX idx_watchlist_user_id ON watchlist_items (user_id);
CREATE INDEX idx_watchlist_ticker  ON watchlist_items (ticker);

-- ---------------------------------------------------------------------------
-- alerts
-- Price threshold, RSI, and volume spike alerts per user ticker.
-- ---------------------------------------------------------------------------
CREATE TABLE alerts (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  ticker       VARCHAR(10) NOT NULL,

  alert_type   VARCHAR(20) NOT NULL
                 CHECK (alert_type IN ('price_above', 'price_below', 'rsi_above', 'rsi_below', 'volume_spike')),

  -- price_above / price_below: threshold in VND
  price_threshold     NUMERIC(12,2),
  -- rsi_above / rsi_below: threshold value (0–100)
  rsi_threshold       NUMERIC(5,2) CHECK (rsi_threshold IS NULL OR (rsi_threshold BETWEEN 0 AND 100)),
  -- volume_spike: multiplier of 20-day average (e.g. 2.0 = 200%)
  volume_multiplier   NUMERIC(6,2) CHECK (volume_multiplier IS NULL OR volume_multiplier > 0),

  is_active    BOOLEAN     NOT NULL DEFAULT TRUE,
  is_repeating BOOLEAN     NOT NULL DEFAULT FALSE,  -- re-arm after trigger

  -- Delivery
  notify_telegram BOOLEAN NOT NULL DEFAULT TRUE,

  last_triggered_at   TIMESTAMPTZ,
  triggered_count     INT         NOT NULL DEFAULT 0,

  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_user_id   ON alerts (user_id);
CREATE INDEX idx_alerts_ticker    ON alerts (ticker);
CREATE INDEX idx_alerts_active    ON alerts (ticker, is_active) WHERE is_active = TRUE;

SELECT attach_updated_at_trigger('alerts');

-- ---------------------------------------------------------------------------
-- alert_deliveries
-- Audit trail of each alert notification sent.
-- ---------------------------------------------------------------------------
CREATE TABLE alert_deliveries (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id    UUID        NOT NULL REFERENCES alerts (id) ON DELETE CASCADE,
  user_id     UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  channel     VARCHAR(20) NOT NULL CHECK (channel IN ('telegram', 'email')),
  status      VARCHAR(20) NOT NULL DEFAULT 'sent'
                CHECK (status IN ('sent', 'delivered', 'failed')),
  triggered_value NUMERIC(12,4),   -- price/RSI/volume at trigger time
  sent_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  error_msg   TEXT
);

CREATE INDEX idx_alert_deliveries_alert_id ON alert_deliveries (alert_id);
CREATE INDEX idx_alert_deliveries_user_id  ON alert_deliveries (user_id);

-- =============================================================================
-- 4. NEWSLETTER & NOTIFICATIONS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- newsletter_campaigns
-- One row per newsletter edition (morning 08:00 or evening 15:30).
-- Content is assembled at send time from market data + optional blog post.
-- ---------------------------------------------------------------------------
CREATE TABLE newsletter_campaigns (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  edition_type      VARCHAR(20) NOT NULL
                      CHECK (edition_type IN ('morning', 'evening')),
  scheduled_at      TIMESTAMPTZ NOT NULL,   -- e.g. 2024-01-15 01:00:00 UTC (= 08:00 UTC+7)
  sent_at           TIMESTAMPTZ,
  status            VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                      CHECK (status IN ('scheduled', 'sending', 'sent', 'failed', 'cancelled')),

  -- Snapshot of market data embedded at send time
  market_snapshot   JSONB,    -- VN-Index, HNX, UPCOM, top gainers/losers, foreign flow
  global_snapshot   JSONB,    -- VIX, USD/VND, Brent, S&P500, Nikkei, Hang Seng

  -- Linked featured blog post (P3)
  featured_post_id  UUID,     -- FK added after blog table definition (see below)

  subject_line      TEXT,
  preview_text      TEXT,

  total_recipients  INT,
  total_sent        INT        NOT NULL DEFAULT 0,
  total_opened      INT        NOT NULL DEFAULT 0,
  total_failed      INT        NOT NULL DEFAULT 0,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_newsletter_campaigns_scheduled ON newsletter_campaigns (scheduled_at);
CREATE INDEX idx_newsletter_campaigns_status    ON newsletter_campaigns (status);

SELECT attach_updated_at_trigger('newsletter_campaigns');

-- ---------------------------------------------------------------------------
-- newsletter_sends
-- One row per user per campaign. Tracks delivery and open state.
-- ---------------------------------------------------------------------------
CREATE TABLE newsletter_sends (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id   UUID        NOT NULL REFERENCES newsletter_campaigns (id) ON DELETE CASCADE,
  user_id       UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,

  channel       VARCHAR(20) NOT NULL DEFAULT 'telegram'
                  CHECK (channel IN ('telegram', 'email')),
  status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')),

  -- Open tracking
  open_token    TEXT        UNIQUE,         -- unique pixel/link token
  opened        BOOLEAN     NOT NULL DEFAULT FALSE,
  opened_at     TIMESTAMPTZ,
  open_count    INT         NOT NULL DEFAULT 0,

  sent_at       TIMESTAMPTZ,
  failed_reason TEXT,

  UNIQUE (campaign_id, user_id, channel)
);

CREATE INDEX idx_newsletter_sends_campaign_id ON newsletter_sends (campaign_id);
CREATE INDEX idx_newsletter_sends_user_id     ON newsletter_sends (user_id);
CREATE INDEX idx_newsletter_sends_open_token  ON newsletter_sends (open_token) WHERE open_token IS NOT NULL;
CREATE INDEX idx_newsletter_sends_status      ON newsletter_sends (status);

-- ---------------------------------------------------------------------------
-- telegram_bot_events
-- Records bot lifecycle events: /start, /login, blocked, unblocked, etc.
-- ---------------------------------------------------------------------------
CREATE TABLE telegram_bot_events (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        REFERENCES users (id) ON DELETE SET NULL,
  chat_id     BIGINT      NOT NULL,
  event_type  VARCHAR(40) NOT NULL
                CHECK (event_type IN (
                  'start', 'login', 'logout', 'status',
                  'bot_blocked', 'bot_unblocked',
                  'message_received', 'command_received'
                )),
  payload     JSONB,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tg_bot_events_user_id    ON telegram_bot_events (user_id);
CREATE INDEX idx_tg_bot_events_chat_id    ON telegram_bot_events (chat_id);
CREATE INDEX idx_tg_bot_events_type       ON telegram_bot_events (event_type);
CREATE INDEX idx_tg_bot_events_occurred   ON telegram_bot_events (occurred_at);

-- =============================================================================
-- 5. MARKET DATA
-- =============================================================================
-- NOTE: Real-time tick data is served from Redis cache.
-- This schema stores EOD data, technical indicators, corporate events, news,
-- and global indicators. All price data is informational only (see DISCLAIMER).

-- ---------------------------------------------------------------------------
-- stock_tickers
-- Master reference list of listed securities.
-- ---------------------------------------------------------------------------
CREATE TABLE stock_tickers (
  ticker          VARCHAR(10) PRIMARY KEY,
  company_name    TEXT        NOT NULL,
  exchange        VARCHAR(10) NOT NULL
                    CHECK (exchange IN ('HOSE', 'HNX', 'UPCOM')),
  sector          TEXT,
  industry        TEXT,
  market_cap_vnd  NUMERIC(20,2),
  is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
  listed_at       DATE,
  delisted_at     DATE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tickers_exchange ON stock_tickers (exchange) WHERE is_active = TRUE;
CREATE INDEX idx_tickers_sector   ON stock_tickers (sector) WHERE is_active = TRUE;

SELECT attach_updated_at_trigger('stock_tickers');

-- ---------------------------------------------------------------------------
-- eod_prices
-- End-of-day OHLCV per ticker. One row per ticker per trading date.
-- ---------------------------------------------------------------------------
CREATE TABLE eod_prices (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker        VARCHAR(10) NOT NULL REFERENCES stock_tickers (ticker) ON DELETE CASCADE,
  trading_date  DATE        NOT NULL,
  open_price    NUMERIC(12,2) NOT NULL CHECK (open_price > 0),
  high_price    NUMERIC(12,2) NOT NULL CHECK (high_price > 0),
  low_price     NUMERIC(12,2) NOT NULL CHECK (low_price > 0),
  close_price   NUMERIC(12,2) NOT NULL CHECK (close_price > 0),
  adj_close     NUMERIC(12,2) CHECK (adj_close > 0),   -- adjusted for dividends/splits
  volume        BIGINT       NOT NULL CHECK (volume >= 0),
  value_vnd     NUMERIC(20,2),                          -- total transaction value
  created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

  UNIQUE (ticker, trading_date),
  CHECK (high_price >= low_price),
  CHECK (high_price >= open_price),
  CHECK (high_price >= close_price),
  CHECK (low_price  <= open_price),
  CHECK (low_price  <= close_price)
);

CREATE INDEX idx_eod_prices_ticker_date  ON eod_prices (ticker, trading_date DESC);
CREATE INDEX idx_eod_prices_trading_date ON eod_prices (trading_date DESC);

-- ---------------------------------------------------------------------------
-- technical_indicators
-- Pre-computed daily indicators: MA20/50/200, RSI14, volume 20-day avg.
-- Populated by a background job after EOD data is loaded.
-- ---------------------------------------------------------------------------
CREATE TABLE technical_indicators (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker          VARCHAR(10) NOT NULL REFERENCES stock_tickers (ticker) ON DELETE CASCADE,
  trading_date    DATE        NOT NULL,

  ma20            NUMERIC(12,2),
  ma50            NUMERIC(12,2),
  ma200           NUMERIC(12,2),
  rsi14           NUMERIC(5,2) CHECK (rsi14 IS NULL OR (rsi14 BETWEEN 0 AND 100)),
  volume_avg_20d  BIGINT,       -- 20-day average daily volume
  volume_ratio    NUMERIC(6,2), -- today_volume / volume_avg_20d

  created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

  UNIQUE (ticker, trading_date)
);

CREATE INDEX idx_tech_indicators_ticker_date ON technical_indicators (ticker, trading_date DESC);

-- ---------------------------------------------------------------------------
-- market_index_eod
-- Daily close for VN-Index, HNX-Index, UPCOM-Index.
-- ---------------------------------------------------------------------------
CREATE TABLE market_index_eod (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  index_code      VARCHAR(10) NOT NULL
                    CHECK (index_code IN ('VN-INDEX', 'HNX-INDEX', 'UPCOM')),
  trading_date    DATE        NOT NULL,
  open_value      NUMERIC(10,2),
  high_value      NUMERIC(10,2),
  low_value       NUMERIC(10,2),
  close_value     NUMERIC(10,2) NOT NULL,
  change_points   NUMERIC(8,2),
  change_pct      NUMERIC(6,2),
  total_volume    BIGINT,
  total_value_vnd NUMERIC(22,2),
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

  UNIQUE (index_code, trading_date)
);

CREATE INDEX idx_mkt_index_eod_date ON market_index_eod (trading_date DESC);

-- ---------------------------------------------------------------------------
-- foreign_investor_flow
-- Daily net buy/sell volume and value by foreign investors per ticker and market.
-- ---------------------------------------------------------------------------
CREATE TABLE foreign_investor_flow (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  trading_date    DATE        NOT NULL,
  ticker          VARCHAR(10) REFERENCES stock_tickers (ticker) ON DELETE CASCADE,
  market          VARCHAR(10) CHECK (market IN ('HOSE', 'HNX', 'UPCOM', 'ALL')),

  buy_volume      BIGINT       NOT NULL DEFAULT 0,
  sell_volume     BIGINT       NOT NULL DEFAULT 0,
  net_volume      BIGINT       GENERATED ALWAYS AS (buy_volume - sell_volume) STORED,

  buy_value_vnd   NUMERIC(20,2) NOT NULL DEFAULT 0,
  sell_value_vnd  NUMERIC(20,2) NOT NULL DEFAULT 0,
  net_value_vnd   NUMERIC(20,2) GENERATED ALWAYS AS (buy_value_vnd - sell_value_vnd) STORED,

  created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

  -- Either ticker-level or market-level row (not both null)
  CHECK (ticker IS NOT NULL OR market IS NOT NULL)
);

CREATE INDEX idx_foreign_flow_date         ON foreign_investor_flow (trading_date DESC);
CREATE INDEX idx_foreign_flow_ticker_date  ON foreign_investor_flow (ticker, trading_date DESC) WHERE ticker IS NOT NULL;
CREATE INDEX idx_foreign_flow_market_date  ON foreign_investor_flow (market, trading_date DESC) WHERE market IS NOT NULL;

-- ---------------------------------------------------------------------------
-- global_market_indicators
-- Daily snapshots of global benchmarks referenced in newsletter.
-- ---------------------------------------------------------------------------
CREATE TABLE global_market_indicators (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  trading_date    DATE        NOT NULL,
  indicator       VARCHAR(20) NOT NULL
                    CHECK (indicator IN ('VIX', 'USD_VND', 'BRENT_OIL', 'SP500', 'NIKKEI225', 'HANG_SENG')),
  close_value     NUMERIC(14,4) NOT NULL,
  change_pct      NUMERIC(6,2),
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

  UNIQUE (trading_date, indicator)
);

CREATE INDEX idx_global_indicators_date ON global_market_indicators (trading_date DESC);

-- ---------------------------------------------------------------------------
-- corporate_events
-- AGM dates, dividend announcements, new listings, etc.
-- Linked to watchlist via ticker for personalised calendar display.
-- ---------------------------------------------------------------------------
CREATE TABLE corporate_events (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker          VARCHAR(10) NOT NULL REFERENCES stock_tickers (ticker) ON DELETE CASCADE,
  event_type      VARCHAR(30) NOT NULL
                    CHECK (event_type IN (
                      'agm', 'egm', 'dividend_cash', 'dividend_stock',
                      'stock_split', 'rights_issue', 'new_listing',
                      'delisting', 'earnings_release', 'other'
                    )),
  event_date      DATE        NOT NULL,
  ex_date         DATE,         -- ex-dividend / ex-rights date
  record_date     DATE,
  payment_date    DATE,

  -- Dividend specifics
  dividend_per_share_vnd NUMERIC(12,2),
  dividend_yield_pct     NUMERIC(5,2),

  title           TEXT        NOT NULL,
  description     TEXT,
  source_url      TEXT,

  is_confirmed    BOOLEAN     NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_corp_events_ticker      ON corporate_events (ticker);
CREATE INDEX idx_corp_events_event_date  ON corporate_events (event_date);
CREATE INDEX idx_corp_events_type        ON corporate_events (event_type);

SELECT attach_updated_at_trigger('corporate_events');

-- ---------------------------------------------------------------------------
-- news_articles
-- AI-analysed news with VN market impact scoring.
-- DISCLAIMER: AI analysis is informational only, not financial advice.
-- ---------------------------------------------------------------------------
CREATE TABLE news_articles (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id     TEXT        UNIQUE,       -- source article ID for dedup
  source_name     TEXT        NOT NULL,
  source_url      TEXT        NOT NULL,
  title           TEXT        NOT NULL,
  summary         TEXT,                     -- extracted plain-text summary
  published_at    TIMESTAMPTZ NOT NULL,

  -- AI analysis (nullable until processed)
  ai_impact       VARCHAR(10) CHECK (ai_impact IN ('positive', 'negative', 'neutral', 'mixed')),
  ai_reason       TEXT,         -- Vietnamese-language explanation of impact
  ai_confidence   NUMERIC(4,2) CHECK (ai_confidence IS NULL OR (ai_confidence BETWEEN 0 AND 1)),
  ai_analysed_at  TIMESTAMPTZ,

  -- Related tickers (array for fast membership check)
  related_tickers TEXT[]      NOT NULL DEFAULT '{}',

  language        VARCHAR(5)  NOT NULL DEFAULT 'vi' CHECK (language IN ('vi', 'en')),
  is_featured     BOOLEAN     NOT NULL DEFAULT FALSE,

  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_news_published_at     ON news_articles (published_at DESC);
CREATE INDEX idx_news_impact           ON news_articles (ai_impact) WHERE ai_impact IS NOT NULL;
CREATE INDEX idx_news_related_tickers  ON news_articles USING GIN (related_tickers);
-- Full-text search on title + summary (Vietnamese + English)
CREATE INDEX idx_news_fts ON news_articles
  USING GIN (to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(summary, '')));

SELECT attach_updated_at_trigger('news_articles');

-- =============================================================================
-- 6. BLOG & CONTENT (Admin/Editor CMS — P3)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- blog_authors
-- CMS user roles. Separate from platform users (can overlap via user_id FK).
-- ---------------------------------------------------------------------------
CREATE TABLE blog_authors (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        UNIQUE REFERENCES users (id) ON DELETE SET NULL,
  pen_name    TEXT        NOT NULL,
  bio         TEXT,
  avatar_url  TEXT,
  role        VARCHAR(20) NOT NULL DEFAULT 'author'
                CHECK (role IN ('admin', 'editor', 'author')),
  is_active   BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_blog_authors_user_id ON blog_authors (user_id) WHERE user_id IS NOT NULL;

SELECT attach_updated_at_trigger('blog_authors');

-- ---------------------------------------------------------------------------
-- blog_categories
-- Hierarchical categories for blog posts.
-- ---------------------------------------------------------------------------
CREATE TABLE blog_categories (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_id   UUID        REFERENCES blog_categories (id) ON DELETE SET NULL,
  slug        TEXT        NOT NULL UNIQUE,
  name        TEXT        NOT NULL,
  description TEXT,
  sort_order  INT         NOT NULL DEFAULT 0,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_blog_categories_parent ON blog_categories (parent_id) WHERE parent_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- blog_posts
-- Admin/Editor CMS posts. Rich-text stored as JSONB blocks; Markdown in content.
-- Workflow: draft → in_review → published | archived | scheduled.
-- ---------------------------------------------------------------------------
CREATE TABLE blog_posts (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id         UUID        NOT NULL REFERENCES blog_authors (id) ON DELETE RESTRICT,
  category_id       UUID        REFERENCES blog_categories (id) ON DELETE SET NULL,

  -- Content
  title             TEXT        NOT NULL,
  slug              TEXT        NOT NULL UNIQUE,
  excerpt           TEXT,
  content_markdown  TEXT,        -- Markdown source
  content_blocks    JSONB,       -- Rich-text block representation (e.g. Tiptap JSON)
  featured_image    TEXT,

  -- SEO fields
  seo_title         TEXT,
  seo_description   TEXT,
  canonical_url     TEXT,
  og_image          TEXT,

  -- Workflow
  status            VARCHAR(20) NOT NULL DEFAULT 'draft'
                      CHECK (status IN ('draft', 'in_review', 'scheduled', 'published', 'archived')),
  review_notes      TEXT,
  scheduled_at      TIMESTAMPTZ,  -- publish at this time when status = scheduled
  published_at      TIMESTAMPTZ,
  archived_at       TIMESTAMPTZ,

  -- Related tickers (for stock detail page aggregation)
  tagged_tickers    TEXT[]      NOT NULL DEFAULT '{}',

  -- Newsletter linking (P3)
  featured_in_campaign_id UUID REFERENCES newsletter_campaigns (id) ON DELETE SET NULL,

  -- Soft delete
  deleted_at        TIMESTAMPTZ,

  -- Stats (denormalised counters, updated by triggers or background job)
  view_count        INT         NOT NULL DEFAULT 0,
  like_count        INT         NOT NULL DEFAULT 0,
  comment_count     INT         NOT NULL DEFAULT 0,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_blog_posts_author          ON blog_posts (author_id);
CREATE INDEX idx_blog_posts_category        ON blog_posts (category_id) WHERE category_id IS NOT NULL;
CREATE INDEX idx_blog_posts_status          ON blog_posts (status) WHERE deleted_at IS NULL;
CREATE INDEX idx_blog_posts_published_at    ON blog_posts (published_at DESC) WHERE status = 'published' AND deleted_at IS NULL;
CREATE INDEX idx_blog_posts_scheduled_at    ON blog_posts (scheduled_at) WHERE status = 'scheduled';
CREATE INDEX idx_blog_posts_tagged_tickers  ON blog_posts USING GIN (tagged_tickers);
CREATE INDEX idx_blog_posts_deleted_at      ON blog_posts (deleted_at) WHERE deleted_at IS NOT NULL;
-- Full-text search on title + excerpt
CREATE INDEX idx_blog_posts_fts ON blog_posts
  USING GIN (to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(excerpt, '')))
  WHERE deleted_at IS NULL;

SELECT attach_updated_at_trigger('blog_posts');

-- ---------------------------------------------------------------------------
-- blog_post_revisions
-- Immutable history of all edits for audit trail.
-- ---------------------------------------------------------------------------
CREATE TABLE blog_post_revisions (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id           UUID        NOT NULL REFERENCES blog_posts (id) ON DELETE CASCADE,
  revised_by        UUID        NOT NULL REFERENCES blog_authors (id) ON DELETE RESTRICT,
  content_markdown  TEXT,
  content_blocks    JSONB,
  status_at_revision VARCHAR(20),
  change_summary    TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_blog_revisions_post_id ON blog_post_revisions (post_id);

-- Now add the FK for featured_post_id on newsletter_campaigns
ALTER TABLE newsletter_campaigns
  ADD CONSTRAINT fk_newsletter_featured_post
  FOREIGN KEY (featured_post_id) REFERENCES blog_posts (id) ON DELETE SET NULL;

CREATE INDEX idx_newsletter_campaigns_featured_post ON newsletter_campaigns (featured_post_id)
  WHERE featured_post_id IS NOT NULL;

-- =============================================================================
-- 7. COMMUNITY & MODERATION (P4)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- community_posts
-- User-generated content. Goes through moderation queue before visibility.
-- ---------------------------------------------------------------------------
CREATE TABLE community_posts (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id         UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,

  title             TEXT        NOT NULL,
  slug              TEXT        NOT NULL UNIQUE,
  content_markdown  TEXT        NOT NULL,
  featured_image    TEXT,

  -- Moderation workflow
  status            VARCHAR(20) NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'approved', 'rejected', 'removed')),
  moderated_by      UUID        REFERENCES users (id) ON DELETE SET NULL,
  moderated_at      TIMESTAMPTZ,
  rejection_reason  TEXT,

  -- Ticker tags
  tagged_tickers    TEXT[]      NOT NULL DEFAULT '{}',

  -- Soft delete
  deleted_at        TIMESTAMPTZ,

  -- Denormalised counters
  view_count        INT         NOT NULL DEFAULT 0,
  like_count        INT         NOT NULL DEFAULT 0,
  comment_count     INT         NOT NULL DEFAULT 0,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_community_posts_author     ON community_posts (author_id);
CREATE INDEX idx_community_posts_status     ON community_posts (status) WHERE deleted_at IS NULL;
CREATE INDEX idx_community_posts_tickers    ON community_posts USING GIN (tagged_tickers);
CREATE INDEX idx_community_posts_deleted    ON community_posts (deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_community_posts_approved   ON community_posts (created_at DESC) WHERE status = 'approved' AND deleted_at IS NULL;
-- Full-text search
CREATE INDEX idx_community_posts_fts ON community_posts
  USING GIN (to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(content_markdown, '')))
  WHERE status = 'approved' AND deleted_at IS NULL;

SELECT attach_updated_at_trigger('community_posts');

-- ---------------------------------------------------------------------------
-- post_comments
-- Threaded comments on both blog_posts and community_posts.
-- Uses a union approach via nullable FKs (one must be non-null).
-- ---------------------------------------------------------------------------
CREATE TABLE post_comments (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id         UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,

  -- Target: one of these must be non-null
  blog_post_id      UUID        REFERENCES blog_posts (id) ON DELETE CASCADE,
  community_post_id UUID        REFERENCES community_posts (id) ON DELETE CASCADE,

  parent_comment_id UUID        REFERENCES post_comments (id) ON DELETE CASCADE,   -- threading
  content           TEXT        NOT NULL,

  status            VARCHAR(20) NOT NULL DEFAULT 'visible'
                      CHECK (status IN ('visible', 'hidden', 'removed')),

  like_count        INT         NOT NULL DEFAULT 0,
  deleted_at        TIMESTAMPTZ,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CHECK (
    (blog_post_id IS NOT NULL AND community_post_id IS NULL) OR
    (blog_post_id IS NULL AND community_post_id IS NOT NULL)
  )
);

CREATE INDEX idx_comments_author        ON post_comments (author_id);
CREATE INDEX idx_comments_blog_post     ON post_comments (blog_post_id) WHERE blog_post_id IS NOT NULL;
CREATE INDEX idx_comments_community     ON post_comments (community_post_id) WHERE community_post_id IS NOT NULL;
CREATE INDEX idx_comments_parent        ON post_comments (parent_comment_id) WHERE parent_comment_id IS NOT NULL;

SELECT attach_updated_at_trigger('post_comments');

-- ---------------------------------------------------------------------------
-- post_likes
-- Likes on blog_posts, community_posts, or comments.
-- ---------------------------------------------------------------------------
CREATE TABLE post_likes (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,

  blog_post_id      UUID        REFERENCES blog_posts (id) ON DELETE CASCADE,
  community_post_id UUID        REFERENCES community_posts (id) ON DELETE CASCADE,
  comment_id        UUID        REFERENCES post_comments (id) ON DELETE CASCADE,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Exactly one target
  CHECK (
    (blog_post_id IS NOT NULL)::INT +
    (community_post_id IS NOT NULL)::INT +
    (comment_id IS NOT NULL)::INT = 1
  ),
  UNIQUE NULLS NOT DISTINCT (user_id, blog_post_id, community_post_id, comment_id)
);

CREATE INDEX idx_likes_user_id          ON post_likes (user_id);
CREATE INDEX idx_likes_blog_post        ON post_likes (blog_post_id) WHERE blog_post_id IS NOT NULL;
CREATE INDEX idx_likes_community_post   ON post_likes (community_post_id) WHERE community_post_id IS NOT NULL;
CREATE INDEX idx_likes_comment          ON post_likes (comment_id) WHERE comment_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- author_follows
-- Users following blog authors or other community users.
-- ---------------------------------------------------------------------------
CREATE TABLE author_follows (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  follower_id       UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  followed_user_id  UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE (follower_id, followed_user_id),
  CHECK (follower_id <> followed_user_id)
);

CREATE INDEX idx_author_follows_follower ON author_follows (follower_id);
CREATE INDEX idx_author_follows_followed ON author_follows (followed_user_id);

-- ---------------------------------------------------------------------------
-- content_reports
-- User reports for content moderation.
-- ---------------------------------------------------------------------------
CREATE TABLE content_reports (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id       UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,

  blog_post_id      UUID        REFERENCES blog_posts (id) ON DELETE CASCADE,
  community_post_id UUID        REFERENCES community_posts (id) ON DELETE CASCADE,
  comment_id        UUID        REFERENCES post_comments (id) ON DELETE CASCADE,
  reported_user_id  UUID        REFERENCES users (id) ON DELETE CASCADE,

  reason            VARCHAR(30) NOT NULL
                      CHECK (reason IN (
                        'spam', 'misinformation', 'hate_speech', 'harassment',
                        'financial_fraud', 'copyright', 'other'
                      )),
  description       TEXT,

  status            VARCHAR(20) NOT NULL DEFAULT 'open'
                      CHECK (status IN ('open', 'reviewing', 'resolved', 'dismissed')),
  resolved_by       UUID        REFERENCES users (id) ON DELETE SET NULL,
  resolved_at       TIMESTAMPTZ,
  resolution_note   TEXT,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reports_reporter       ON content_reports (reporter_id);
CREATE INDEX idx_reports_status         ON content_reports (status) WHERE status IN ('open', 'reviewing');
CREATE INDEX idx_reports_blog_post      ON content_reports (blog_post_id) WHERE blog_post_id IS NOT NULL;
CREATE INDEX idx_reports_community_post ON content_reports (community_post_id) WHERE community_post_id IS NOT NULL;

SELECT attach_updated_at_trigger('content_reports');

-- ---------------------------------------------------------------------------
-- user_badges
-- Achievement badges (e.g. "Verified Analyst").
-- ---------------------------------------------------------------------------
CREATE TABLE badges (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  slug        VARCHAR(40) NOT NULL UNIQUE,
  name        TEXT        NOT NULL,
  description TEXT,
  icon_url    TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_badges (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  badge_id    UUID        NOT NULL REFERENCES badges (id) ON DELETE CASCADE,
  awarded_by  UUID        REFERENCES users (id) ON DELETE SET NULL,
  awarded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  note        TEXT,

  UNIQUE (user_id, badge_id)
);

CREATE INDEX idx_user_badges_user_id  ON user_badges (user_id);
CREATE INDEX idx_user_badges_badge_id ON user_badges (badge_id);

-- Seed system badges
INSERT INTO badges (slug, name, description)
VALUES
  ('verified_analyst',  'Verified Analyst',   'Verified financial analyst credential'),
  ('top_contributor',   'Top Contributor',     'Among top 10% of community contributors'),
  ('early_adopter',     'Early Adopter',       'Joined during platform beta'),
  ('referral_champion', 'Referral Champion',   'Successfully referred 10+ users')
ON CONFLICT (slug) DO NOTHING;

-- =============================================================================
-- 8. ANALYTICS
-- =============================================================================
-- 21 tracked events. Append-only event stream.
-- No UPDATE/DELETE — immutable audit log.

-- ---------------------------------------------------------------------------
-- analytics_events
-- ---------------------------------------------------------------------------
CREATE TABLE analytics_events (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID        REFERENCES users (id) ON DELETE SET NULL,
  session_id    TEXT,          -- client-side session identifier
  event_name    VARCHAR(60) NOT NULL
                  CHECK (event_name IN (
                    -- Onboarding / Auth
                    'user_registered',
                    'google_oauth_completed',
                    'telegram_linked',
                    'onboarding_completed',
                    -- Bot
                    'bot_start_command',
                    'bot_login_command',
                    'bot_status_command',
                    'bot_blocked',
                    'bot_unblocked',
                    -- Newsletter
                    'newsletter_sent',
                    'newsletter_opened',
                    'newsletter_link_clicked',
                    -- Alerts
                    'alert_created',
                    'alert_triggered',
                    -- Subscription
                    'subscription_started',
                    'subscription_cancelled',
                    'payment_initiated',
                    'payment_completed',
                    'payment_failed',
                    -- Community
                    'post_published',
                    'referral_completed'
                  )),
  properties    JSONB        NOT NULL DEFAULT '{}',
  platform      VARCHAR(10) NOT NULL DEFAULT 'web'
                  CHECK (platform IN ('web', 'telegram', 'api')),
  ip_address    INET,          -- stored for fraud detection; anonymised after 90 days
  user_agent    TEXT,
  occurred_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Partitioning recommendation: partition by occurred_at range (monthly) for large scale.
-- Applied at infrastructure level; schema kept simple here.

CREATE INDEX idx_analytics_user_id     ON analytics_events (user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_analytics_event_name  ON analytics_events (event_name);
CREATE INDEX idx_analytics_occurred_at ON analytics_events (occurred_at DESC);
CREATE INDEX idx_analytics_session_id  ON analytics_events (session_id) WHERE session_id IS NOT NULL;
-- JSONB property queries (e.g. campaign_id, ticker)
CREATE INDEX idx_analytics_properties  ON analytics_events USING GIN (properties);

-- =============================================================================
-- 9. REFERRAL & NPS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- referral_events
-- Tracks each successful referral (new user completed onboarding via referral link).
-- Bonus watchlist slots are added to users.bonus_watchlist_slots by application.
-- ---------------------------------------------------------------------------
CREATE TABLE referral_events (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  referrer_id     UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  referred_id     UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'qualified', 'rewarded', 'reversed')),
  -- Qualification: referred user must complete onboarding
  qualified_at    TIMESTAMPTZ,
  rewarded_at     TIMESTAMPTZ,
  -- Reward: +1 watchlist slot
  reward_type     VARCHAR(30) DEFAULT 'watchlist_slot_plus_1',
  reversed_at     TIMESTAMPTZ,
  reverse_reason  TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE (referrer_id, referred_id)
);

CREATE INDEX idx_referral_events_referrer ON referral_events (referrer_id);
CREATE INDEX idx_referral_events_referred ON referral_events (referred_id);
CREATE INDEX idx_referral_events_status   ON referral_events (status);

-- ---------------------------------------------------------------------------
-- nps_surveys
-- NPS survey auto-sent via Telegram bot 30 days after registration.
-- Score: 0–10 (detractor <7, passive 7-8, promoter 9-10).
-- ---------------------------------------------------------------------------
CREATE TABLE nps_surveys (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  sent_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  responded_at    TIMESTAMPTZ,
  score           SMALLINT    CHECK (score IS NULL OR (score BETWEEN 0 AND 10)),
  category        VARCHAR(10) GENERATED ALWAYS AS (
                    CASE
                      WHEN score IS NULL    THEN NULL
                      WHEN score <= 6       THEN 'detractor'
                      WHEN score <= 8       THEN 'passive'
                      ELSE                       'promoter'
                    END
                  ) STORED,
  feedback_text   TEXT,
  channel         VARCHAR(20) NOT NULL DEFAULT 'telegram'
                    CHECK (channel IN ('telegram', 'email')),
  survey_version  VARCHAR(10) NOT NULL DEFAULT 'v1',

  UNIQUE (user_id, survey_version)
);

CREATE INDEX idx_nps_surveys_user_id     ON nps_surveys (user_id);
CREATE INDEX idx_nps_surveys_sent_at     ON nps_surveys (sent_at DESC);
CREATE INDEX idx_nps_surveys_category    ON nps_surveys (category) WHERE category IS NOT NULL;
CREATE INDEX idx_nps_surveys_unanswered  ON nps_surveys (sent_at) WHERE responded_at IS NULL;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
-- Summary of tables (39 total):
--
-- Auth & Users (3):
--   users, oauth_sessions, telegram_onboarding_tokens
--
-- Subscriptions & Payments (3):
--   subscription_plans, user_subscriptions, payment_transactions
--
-- Watchlist & Alerts (3):
--   watchlist_items, alerts, alert_deliveries
--
-- Newsletter & Notifications (3):
--   newsletter_campaigns, newsletter_sends, telegram_bot_events
--
-- Market Data (8):
--   stock_tickers, eod_prices, technical_indicators, market_index_eod,
--   foreign_investor_flow, global_market_indicators, corporate_events,
--   news_articles
--
-- Blog & Content (4):
--   blog_authors, blog_categories, blog_posts, blog_post_revisions
--
-- Community & Moderation (8):
--   community_posts, post_comments, post_likes, author_follows,
--   content_reports, badges, user_badges,
--   (newsletter_campaigns.featured_post_id FK added via ALTER TABLE)
--
-- Analytics (1):
--   analytics_events
--
-- Referral & NPS (2):
--   referral_events, nps_surveys
-- =============================================================================
