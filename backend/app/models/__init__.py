# Import all models so Alembic can detect them via Base.metadata
# Order matters: import parent tables before child tables (FK dependencies)
from app.models.user import OAuthSession, TelegramOnboardingToken, User
from app.models.subscription import SubscriptionPlan, UserSubscription
from app.models.watchlist import WatchlistItem
from app.models.newsletter import NewsletterCampaign, NewsletterSend, TelegramBotEvent
from app.models.market_data import StockTicker
from app.models.analytics import AnalyticsEvent

__all__ = [
    "User",
    "OAuthSession",
    "TelegramOnboardingToken",
    "SubscriptionPlan",
    "UserSubscription",
    "WatchlistItem",
    "NewsletterCampaign",
    "NewsletterSend",
    "TelegramBotEvent",
    "StockTicker",
    "AnalyticsEvent",
]
