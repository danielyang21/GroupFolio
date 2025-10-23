"""Constants and configuration values for GroupFolio bot"""


class Limits:
    """Display and data limits"""
    MAX_WATCHLIST_DISPLAY = 10
    MAX_WATCHLIST_SIZE = 25
    MAX_PORTFOLIO_POSITIONS_DISPLAY = 10
    MAX_TRANSACTIONS_DISPLAY = 50
    DEFAULT_TRANSACTIONS_DISPLAY = 10
    MAX_LEADERBOARD_DISPLAY = 10
    MAX_EARNINGS_DISPLAY = 15


class Timeouts:
    """Timeout values in seconds"""
    CHART_BUTTON_TIMEOUT = 300
    CONFIRMATION_TIMEOUT = 120
    API_REQUEST_TIMEOUT = 30
    STOCK_FETCH_TIMEOUT = 30
    CHART_GENERATION_TIMEOUT = 45
    LEADERBOARD_COOLDOWN = 30
    CALENDAR_COOLDOWN = 60
    WATCHLIST_COOLDOWN = 10
    CHART_COOLDOWN = 5


class TradingDefaults:
    """Paper trading default values"""
    STARTING_BALANCE = 100_000.00
    MIN_ORDER_QUANTITY = 1
    MAX_ORDER_SIZE = 1_000_000


class ChartSettings:
    """Chart generation settings"""
    VALID_PERIODS = ['1d', '1mo', '3mo', 'ytd', '1y', '5y']
    DEFAULT_PERIOD = '1mo'

    PERIOD_NAMES = {
        '1d': '1 Day',
        '1mo': '1 Month',
        '3mo': '3 Months',
        'ytd': 'Year to Date',
        '1y': '1 Year',
        '5y': '5 Years'
    }

    PERIOD_INTERVALS = {
        '1d': '5m',
        '1mo': '1d',
        '3mo': '1d',
        'ytd': '1d',
        '1y': '1wk',
        '5y': '1mo'
    }

    CHART_WIDTH = 12
    CHART_HEIGHT = 6
    CHART_DPI = 100
    MA_SHORT = 20
    MA_LONG = 50


class Colors:
    """Discord embed colors"""
    SUCCESS = 0x57f287
    ERROR = 0xed4245
    WARNING = 0xfee75c
    INFO = 0x5865f2
    NEUTRAL = 0x99aab5


class Emojis:
    """Consistent emoji usage across bot"""
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    LOADING = "⏳"
    INFO = "ℹ️"
    UP = "📈"
    DOWN = "📉"
    NEUTRAL_TREND = "➡️"
    GREEN_CIRCLE = "🟢"
    RED_CIRCLE = "🔴"
    WHITE_CIRCLE = "⚪"
    CHART = "📊"
    CALENDAR = "📅"
    MONEY = "💰"
    TROPHY = "🏆"
    FIRE = "🔥"
    PORTFOLIO = "💼"
    TRANSACTION = "📜"


class Messages:
    """Standard message templates"""
    # Database errors
    DB_NOT_CONNECTED = """❌ **Database not connected!**

To save data, you need to:
1. Set up MongoDB Atlas (free at mongodb.com)
2. Add `MONGODB_URI` to your `.env` file
3. Restart the bot

Check `DEPLOYMENT.md` for detailed instructions."""

    # Validation errors
    INVALID_SYMBOL_TEMPLATE = """❌ Invalid stock symbol: `{}`

**Tips:**
• Canadian stocks: Add `.TO` (e.g., `VFV.TO`, `SHOP.TO`)
• US stocks: Use plain symbol (e.g., `AAPL`, `TSLA`)
• ETFs work too! (e.g., `SPY`, `QQQ`, `VFV.TO`)"""

    INVALID_PERIOD_TEMPLATE = """❌ Invalid time period: `{}`

**Valid periods:** {valid_periods}

**Examples:**
• `!stock AAPL` - 1 month (default)
• `!stock AAPL 1y` - 1 year
• `!stock AAPL ytd` - Year to date"""

    # Success messages
    STOCK_ADDED_TEMPLATE = "✅ Added **{symbol}** to the watchlist"
    STOCK_REMOVED_TEMPLATE = "✅ Removed **{symbol}** from the watchlist"

    # Generic errors
    COMMAND_ON_COOLDOWN = "⏳ Slow down! Try again in {:.1f} seconds."
    OPERATION_TIMEOUT = "❌ Operation timed out. Please try again."
    GENERIC_ERROR = "❌ An unexpected error occurred. Please try again."
