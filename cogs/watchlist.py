"""
Watchlist commands cog - manage group stock watchlists
"""
import discord
from discord.ext import commands
import config
from utils import database, stock_api


class Watchlist(commands.Cog):
    """Group watchlist management commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='addstock', aliases=['add', 'watch'])
    async def add_stock(self, ctx, symbol: str):
        """
        Add a stock to the server's watchlist

        Usage: !addstock AAPL
        """
        # Convert to uppercase
        symbol = symbol.upper()

        # Validate the stock symbol first
        await ctx.send(f"⏳ Validating {symbol}...")

        stock_info = await stock_api.get_stock_info(symbol)

        if not stock_info:
            error_msg = f"❌ Invalid stock symbol: `{symbol}`\n\n"
            error_msg += "**Tips:**\n"
            error_msg += "• Canadian stocks: Add `.TO` (e.g., `VFV.TO`, `SHOP.TO`)\n"
            error_msg += "• US stocks: Use plain symbol (e.g., `AAPL`, `TSLA`)\n"
            error_msg += "• ETFs work too! (e.g., `SPY`, `QQQ`, `VFV.TO`)"
            await ctx.send(error_msg)
            return

        # Add to database
        success, error = await database.add_stock_to_watchlist(
            guild_id=ctx.guild.id,
            symbol=symbol,
            added_by_id=ctx.author.id,
            added_by_name=ctx.author.name
        )

        if not success:
            if error == "database_not_connected":
                await ctx.send(f"❌ Database is not connected!\n\nTo save watchlists, you need to:\n1. Set up MongoDB Atlas (free)\n2. Add `MONGODB_URI` to your `.env` file\n3. Restart the bot")
            elif error == "already_exists":
                await ctx.send(f"❌ `{symbol}` is already in the watchlist!")
            else:
                await ctx.send(f"❌ Failed to add `{symbol}` to the watchlist")
            return

        # Create success embed with stock info
        embed = discord.Embed(
            title=f"✅ Added {stock_info['name']}",
            description=f"**{symbol}** has been added to the watchlist",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Current Price",
            value=stock_api.format_price(stock_info['price'], stock_info['currency']),
            inline=True
        )

        embed.add_field(
            name="Change",
            value=stock_api.format_change(stock_info['change'], stock_info['change_percent']),
            inline=True
        )

        embed.set_footer(text=f"Added by {ctx.author.name}")

        await ctx.send(embed=embed)

    @commands.command(name='removestock', aliases=['remove', 'unwatch', 'rm'])
    async def remove_stock(self, ctx, symbol: str):
        """
        Remove a stock from the server's watchlist

        Usage: !removestock AAPL
        """
        symbol = symbol.upper()

        success = await database.remove_stock_from_watchlist(
            guild_id=ctx.guild.id,
            symbol=symbol
        )

        if success:
            await ctx.send(f"✅ Removed **{symbol}** from the watchlist")
        else:
            await ctx.send(f"❌ **{symbol}** is not in the watchlist")

    @commands.command(name='watchlist', aliases=['wl', 'stocks', 'list'])
    async def view_watchlist(self, ctx):
        """
        View the server's stock watchlist with current prices

        Usage: !watchlist
        """
        stocks = await database.get_watchlist_stocks(ctx.guild.id)

        if not stocks:
            embed = discord.Embed(
                title="📊 Server Watchlist",
                description=f"No stocks in the watchlist yet!\n\nUse `{config.COMMAND_PREFIX}addstock <SYMBOL>` to add one.",
                color=config.BOT_COLOR
            )
            embed.set_thumbnail(url="https://i.imgur.com/wSTFkRM.png")  # Chart icon
            await ctx.send(embed=embed)
            return

        # Fetch current prices for all stocks
        loading_msg = await ctx.send(f"⏳ Fetching data for {len(stocks)} stocks...")

        # Fetch all stocks in parallel for much faster performance
        import asyncio
        symbols = [stock['symbol'] for stock in stocks[:25]]  # Limit to 25 stocks

        # Create tasks for parallel fetching
        tasks = [stock_api.get_stock_info(symbol) for symbol in symbols]

        # Fetch all at once (parallel)
        results = await asyncio.gather(*tasks)

        # Calculate overall stats
        total_gainers = 0
        total_losers = 0
        stock_data = []

        for stock_info in results:
            if stock_info:
                stock_data.append(stock_info)
                if stock_info['change'] > 0:
                    total_gainers += 1
                elif stock_info['change'] < 0:
                    total_losers += 1

        # Delete loading message
        await loading_msg.delete()

        # Create main embed
        embed = discord.Embed(
            title=f"📊 {ctx.guild.name}'s Watchlist",
            description=f"```📈 {total_gainers} Gainers  |  📉 {total_losers} Losers  |  📊 {len(stocks)} Total```",
            color=discord.Color.green() if total_gainers > total_losers else discord.Color.red() if total_losers > total_gainers else config.BOT_COLOR,
            timestamp=discord.utils.utcnow()
        )

        # Add stocks as fields for better mobile support
        for stock_info in stock_data[:10]:
            symbol = stock_info['symbol']
            price = stock_info['price']
            change = stock_info['change']
            change_percent = stock_info['change_percent']

            # Format change properly
            if change > 0:
                change_str = f"+${change:.2f} (+{change_percent:.2f}%)"
                emoji = "🟢"
            elif change < 0:
                change_str = f"-${abs(change):.2f} ({change_percent:.2f}%)"
                emoji = "🔴"
            else:
                change_str = f"${change:.2f} ({change_percent:.2f}%)"
                emoji = "⚪"

            price_str = f"${price:,.2f}"

            # Use fields with inline for responsive layout
            embed.add_field(
                name=f"{emoji} {symbol}",
                value=f"**{price_str}**\n{change_str}",
                inline=True
            )

        # Add unavailable stocks
        for stock in stocks[len(stock_data):10]:
            embed.add_field(
                name=f"⚠️ {stock['symbol']}",
                value="Data unavailable",
                inline=True
            )

        # Footer with helpful info
        if len(stocks) > 10:
            embed.set_footer(
                text=f"Showing 10 of {len(stocks)} stocks • Use !stock <SYMBOL> for details",
                icon_url=ctx.guild.icon.url if ctx.guild.icon else None
            )
        else:
            embed.set_footer(
                text=f"Use !addstock <SYMBOL> to add more • !removestock <SYMBOL> to remove",
                icon_url=ctx.guild.icon.url if ctx.guild.icon else None
            )

        await ctx.send(embed=embed)

    @commands.command(name='stock', aliases=['quote', 'price'])
    async def stock_info(self, ctx, symbol: str):
        """
        Get detailed information about a specific stock

        Usage: !stock AAPL
        """
        symbol = symbol.upper()

        await ctx.send(f"⏳ Fetching data for {symbol}...")

        stock_info = await stock_api.get_stock_info(symbol)

        if not stock_info:
            await ctx.send(f"❌ Could not find information for `{symbol}`")
            return

        # Create detailed embed
        embed = discord.Embed(
            title=f"{stock_info['symbol']} - {stock_info['name']}",
            color=discord.Color.green() if stock_info['change'] >= 0 else discord.Color.red()
        )

        # Price and change
        price_str = stock_api.format_price(stock_info['price'], stock_info['currency'])
        change_str = stock_api.format_change(stock_info['change'], stock_info['change_percent'])

        embed.add_field(name="Price", value=price_str, inline=True)
        embed.add_field(name="Change (Day)", value=change_str, inline=True)

        # Market cap if available
        if stock_info.get('market_cap'):
            market_cap = stock_info['market_cap']
            if market_cap >= 1_000_000_000:
                market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:
                market_cap_str = f"${market_cap / 1_000_000:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"

            embed.add_field(name="Market Cap", value=market_cap_str, inline=True)

        # Volume if available
        if stock_info.get('volume'):
            volume_str = f"{stock_info['volume']:,}"
            embed.add_field(name="Volume", value=volume_str, inline=True)

        embed.set_footer(text="Data provided by Yahoo Finance")

        await ctx.send(embed=embed)


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(Watchlist(bot))
