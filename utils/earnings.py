"""
Earnings calendar utilities
"""
import yfinance as yf
from datetime import datetime, timedelta


async def get_stock_earnings(symbol):
    """
    Get earnings information for a stock

    Args:
        symbol (str): Stock symbol

    Returns:
        dict: Earnings data or None if not available
    """
    try:
        ticker = yf.Ticker(symbol)

        # Get earnings dates
        earnings_dates = ticker.earnings_dates

        if earnings_dates is None or earnings_dates.empty:
            return None

        # Get the next upcoming earnings date
        # Make today timezone-aware to match earnings_dates
        import pytz
        today = datetime.now(pytz.UTC)
        future_earnings = earnings_dates[earnings_dates.index > today]

        if future_earnings.empty:
            # No future earnings, get the most recent
            latest_earnings = earnings_dates.iloc[0]
            is_upcoming = False
            earnings_date = latest_earnings.name
        else:
            # Get the next earnings date
            latest_earnings = future_earnings.iloc[-1]  # Most recent future date
            is_upcoming = True
            earnings_date = latest_earnings.name

        # Get EPS data if available
        eps_estimate = latest_earnings.get('EPS Estimate', None)
        eps_actual = latest_earnings.get('Reported EPS', None)

        return {
            'symbol': symbol.upper(),
            'date': earnings_date,
            'is_upcoming': is_upcoming,
            'eps_estimate': eps_estimate,
            'eps_actual': eps_actual
        }

    except Exception as e:
        print(f"Error fetching earnings for {symbol}: {e}")
        return None


async def get_watchlist_earnings(symbols):
    """
    Get earnings calendar for multiple stocks

    Args:
        symbols (list): List of stock symbols

    Returns:
        list: List of earnings data sorted by date
    """
    import asyncio

    # Fetch earnings for all symbols
    tasks = [get_stock_earnings(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)

    # Filter out None results and keep only upcoming earnings
    upcoming_earnings = []
    for earnings in results:
        if earnings and earnings['is_upcoming']:
            upcoming_earnings.append(earnings)

    # Sort by date
    upcoming_earnings.sort(key=lambda x: x['date'])

    return upcoming_earnings


def format_earnings_date(date):
    """
    Format earnings date for display

    Args:
        date (datetime): Earnings date

    Returns:
        str: Formatted date string
    """
    if not isinstance(date, datetime):
        date = date.to_pydatetime()

    # Make dates timezone-naive for comparison
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)

    today = datetime.now()
    days_until = (date - today).days

    # Format date
    date_str = date.strftime("%b %d, %Y")

    # Add relative time
    if days_until == 0:
        relative = "Today"
    elif days_until == 1:
        relative = "Tomorrow"
    elif days_until < 7:
        relative = f"in {days_until} days"
    elif days_until < 30:
        weeks = days_until // 7
        relative = f"in {weeks} week{'s' if weeks > 1 else ''}"
    else:
        months = days_until // 30
        relative = f"in {months} month{'s' if months > 1 else ''}"

    return f"{date_str} ({relative})"
