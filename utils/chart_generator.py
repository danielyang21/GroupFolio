"""
Stock chart generation utilities
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from io import BytesIO
import discord


async def generate_stock_chart(symbol, period="1mo"):
    """
    Generate a stock price chart

    Args:
        symbol (str): Stock symbol
        period (str): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y)

    Returns:
        discord.File: Chart image as Discord file, or None if failed
    """
    try:
        # Fetch historical data
        ticker = yf.Ticker(symbol)

        # Map period to appropriate interval
        interval_map = {
            '1d': '5m',
            '5d': '15m',
            '1mo': '1d',
            '3mo': '1d',
            '6mo': '1wk',
            '1y': '1wk',
            '5y': '1mo'
        }

        interval = interval_map.get(period, '1d')
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return None

        # Get stock info for title
        info = ticker.info
        stock_name = info.get('longName', info.get('shortName', symbol))

        # Create figure with dark theme
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#2b2d31')
        ax.set_facecolor('#1e1f22')

        # Plot closing price
        ax.plot(hist.index, hist['Close'], color='#5865f2', linewidth=2, label='Price')

        # Add moving averages for longer periods
        if period in ['3mo', '6mo', '1y', '5y']:
            if len(hist) >= 20:
                ma20 = hist['Close'].rolling(window=20).mean()
                ax.plot(hist.index, ma20, color='#57f287', linewidth=1.5,
                       linestyle='--', alpha=0.7, label='20 MA')

            if len(hist) >= 50:
                ma50 = hist['Close'].rolling(window=50).mean()
                ax.plot(hist.index, ma50, color='#fee75c', linewidth=1.5,
                       linestyle='--', alpha=0.7, label='50 MA')

        # Formatting
        ax.set_title(f'{symbol} - {stock_name}', fontsize=16, fontweight='bold',
                    color='white', pad=20)
        ax.set_xlabel('Date', fontsize=12, color='#b5bac1')
        ax.set_ylabel('Price (USD)', fontsize=12, color='#b5bac1')

        # Format x-axis dates
        if period == '1d':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        elif period in ['5d', '1mo']:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

        # Rotate dates
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Grid
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)

        # Legend
        if period in ['3mo', '6mo', '1y', '5y']:
            ax.legend(loc='upper left', framealpha=0.9, facecolor='#2b2d31',
                     edgecolor='#5865f2')

        # Calculate and display performance
        first_price = hist['Close'].iloc[0]
        last_price = hist['Close'].iloc[-1]
        change = last_price - first_price
        change_pct = (change / first_price) * 100

        # Performance text
        color = '#57f287' if change >= 0 else '#ed4245'
        sign = '+' if change >= 0 else ''
        perf_text = f'{sign}${change:.2f} ({sign}{change_pct:.2f}%)'

        ax.text(0.02, 0.98, f'Performance: {perf_text}',
               transform=ax.transAxes, fontsize=12, verticalalignment='top',
               color=color, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='#2b2d31', alpha=0.8,
                        edgecolor=color, linewidth=2))

        # Tight layout
        plt.tight_layout()

        # Save to bytes
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor='#2b2d31')
        buf.seek(0)
        plt.close(fig)

        # Create Discord file
        file = discord.File(buf, filename=f'{symbol}_{period}.png')
        return file

    except Exception as e:
        print(f"Error generating chart for {symbol}: {e}")
        return None


def get_period_display(period):
    """Get human-readable period name"""
    period_names = {
        '1d': '1 Day',
        '5d': '5 Days',
        '1mo': '1 Month',
        '3mo': '3 Months',
        '6mo': '6 Months',
        '1y': '1 Year',
        '5y': '5 Years'
    }
    return period_names.get(period, period)
