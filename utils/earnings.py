"""Earnings calendar utilities"""
import yfinance as yf
from datetime import datetime, timedelta


async def get_stock_earnings(symbol):
    """Get earnings information for a stock"""
    try:
        ticker = yf.Ticker(symbol)
        earnings_dates = ticker.earnings_dates

        if earnings_dates is None or earnings_dates.empty:
            return None

        import pytz
        today = datetime.now(pytz.UTC)
        future_earnings = earnings_dates[earnings_dates.index > today]

        if future_earnings.empty:
            latest_earnings = earnings_dates.iloc[0]
            is_upcoming = False
            earnings_date = latest_earnings.name
        else:
            latest_earnings = future_earnings.iloc[-1]
            is_upcoming = True
            earnings_date = latest_earnings.name

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
    """Get earnings calendar for multiple stocks"""
    import asyncio

    tasks = [get_stock_earnings(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)

    upcoming_earnings = []
    for earnings in results:
        if earnings and earnings['is_upcoming']:
            upcoming_earnings.append(earnings)

    upcoming_earnings.sort(key=lambda x: x['date'])

    return upcoming_earnings


def format_earnings_date(date):
    """Format earnings date for display with relative time"""
    if not isinstance(date, datetime):
        date = date.to_pydatetime()

    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)

    today = datetime.now()
    days_until = (date - today).days

    date_str = date.strftime("%b %d, %Y")

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
