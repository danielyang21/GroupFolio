"""Stock API utilities using yfinance"""
import yfinance as yf


async def get_stock_info(symbol):
    """Get stock information and price data"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info or 'regularMarketPrice' not in info:
            hist = ticker.history(period="1d")
            if hist.empty:
                return None

            current_price = hist['Close'].iloc[-1]
            return {
                'symbol': symbol.upper(),
                'name': info.get('longName', symbol.upper()),
                'price': round(current_price, 2),
                'currency': info.get('currency', 'USD'),
                'change': 0,
                'change_percent': 0
            }

        current_price = info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', current_price)
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0

        return {
            'symbol': symbol.upper(),
            'name': info.get('longName', info.get('shortName', symbol.upper())),
            'price': round(current_price, 2),
            'currency': info.get('currency', 'USD'),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'market_cap': info.get('marketCap'),
            'volume': info.get('volume')
        }

    except Exception as e:
        print(f"Error fetching stock info for {symbol}: {e}")
        return None


async def validate_symbol(symbol):
    """Check if a stock symbol is valid"""
    info = await get_stock_info(symbol)
    return info is not None


def format_price(price, currency='USD'):
    """Format price with currency symbol"""
    symbols = {
        'USD': '$',
        'CAD': 'C$',
        'EUR': '€',
        'GBP': '£'
    }

    symbol = symbols.get(currency, '$')
    return f"{symbol}{price:,.2f}"


def format_change(change, change_percent):
    """Format price change with emoji indicator"""
    if change > 0:
        emoji = "📈"
        sign = "+"
    elif change < 0:
        emoji = "📉"
        sign = ""
    else:
        emoji = "➡️"
        sign = ""

    return f"{emoji} {sign}${change:.2f} ({sign}{change_percent:.2f}%)"
