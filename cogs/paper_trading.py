"""
Paper trading commands cog - virtual stock trading
"""
import discord
from discord.ext import commands
import config
from utils import paper_trading, stock_api


class PaperTrading(commands.Cog):
    """Virtual stock trading commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='balance', aliases=['cash', 'money'])
    async def balance(self, ctx):
        """
        Check your virtual cash balance

        Usage: !balance
        """
        account = await paper_trading.get_user_account(ctx.author.id, ctx.guild.id)

        if not account:
            await ctx.send("❌ Database not connected!")
            return

        embed = discord.Embed(
            title=f"💰 {ctx.author.name}'s Balance",
            color=config.BOT_COLOR
        )

        embed.add_field(
            name="Cash",
            value=f"${account['cash']:,.2f}",
            inline=True
        )

        total_value = account['cash']
        positions = account.get('positions', [])

        if positions:
            holdings_value = 0
            for position in positions:
                stock_info = await stock_api.get_stock_info(position['symbol'])
                if stock_info:
                    holdings_value += stock_info['price'] * position['quantity']

            total_value += holdings_value

            embed.add_field(
                name="Holdings Value",
                value=f"${holdings_value:,.2f}",
                inline=True
            )

        embed.add_field(
            name="Total Portfolio Value",
            value=f"${total_value:,.2f}",
            inline=True
        )

        profit_loss = total_value - paper_trading.STARTING_BALANCE
        profit_pct = (profit_loss / paper_trading.STARTING_BALANCE) * 100

        color_emoji = "🟢" if profit_loss >= 0 else "🔴"
        sign = "+" if profit_loss >= 0 else ""

        embed.add_field(
            name="Total P/L",
            value=f"{color_emoji} {sign}${profit_loss:,.2f} ({sign}{profit_pct:.2f}%)",
            inline=False
        )

        embed.set_footer(text=f"Starting balance: ${paper_trading.STARTING_BALANCE:,.2f}")

        await ctx.send(embed=embed)

    @commands.command(name='buy')
    async def buy(self, ctx, symbol: str, quantity: int):
        """
        Buy shares of a stock with virtual money

        Usage: !buy AAPL 10
        """
        if quantity <= 0:
            await ctx.send("❌ Quantity must be positive!")
            return

        symbol = symbol.upper()

        await ctx.send(f"⏳ Fetching current price for {symbol}...")
        stock_info = await stock_api.get_stock_info(symbol)

        if not stock_info:
            await ctx.send(f"❌ Invalid stock symbol: `{symbol}`")
            return

        price = stock_info['price']
        total_cost = price * quantity

        success, message = await paper_trading.buy_stock(
            ctx.author.id,
            ctx.guild.id,
            symbol,
            quantity,
            price
        )

        if success:
            embed = discord.Embed(
                title="✅ Purchase Successful",
                description=f"**{symbol}** - {stock_info['name']}",
                color=discord.Color.green()
            )

            embed.add_field(name="Quantity", value=quantity, inline=True)
            embed.add_field(name="Price per Share", value=f"${price:,.2f}", inline=True)
            embed.add_field(name="Total Cost", value=f"${total_cost:,.2f}", inline=True)

            embed.set_footer(text=f"Purchased by {ctx.author.name}")

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ {message}")

    @commands.command(name='sell')
    async def sell(self, ctx, symbol: str, quantity: int):
        """
        Sell shares of a stock

        Usage: !sell AAPL 5
        """
        if quantity <= 0:
            await ctx.send("❌ Quantity must be positive!")
            return

        symbol = symbol.upper()

        await ctx.send(f"⏳ Fetching current price for {symbol}...")
        stock_info = await stock_api.get_stock_info(symbol)

        if not stock_info:
            await ctx.send(f"❌ Invalid stock symbol: `{symbol}`")
            return

        price = stock_info['price']

        success, message = await paper_trading.sell_stock(
            ctx.author.id,
            ctx.guild.id,
            symbol,
            quantity,
            price
        )

        if success:
            embed = discord.Embed(
                title="✅ Sale Successful",
                description=message,
                color=discord.Color.blue()
            )

            embed.set_footer(text=f"Sold by {ctx.author.name}")

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ {message}")

    @commands.command(name='myportfolio', aliases=['portfolio', 'holdings', 'positions'])
    async def my_portfolio(self, ctx, user: discord.Member = None):
        """
        View your paper trading portfolio (or another user's)

        Usage: !myportfolio
        Usage: !myportfolio @user
        """
        target_user = user or ctx.author
        account = await paper_trading.get_user_account(target_user.id, ctx.guild.id)

        if not account:
            await ctx.send("❌ Database not connected!")
            return

        positions = account.get('positions', [])

        if not positions:
            embed = discord.Embed(
                title=f"📊 {target_user.name}'s Portfolio",
                description=f"No positions yet!\n\nCash: ${account['cash']:,.2f}\n\nUse `!buy <SYMBOL> <QUANTITY>` to start trading!",
                color=config.BOT_COLOR
            )
            await ctx.send(embed=embed)
            return

        loading_msg = await ctx.send(f"⏳ Fetching data for {len(positions)} positions...")

        import asyncio
        symbols = [p['symbol'] for p in positions]
        tasks = [stock_api.get_stock_info(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)

        total_value = account['cash']
        total_cost_basis = 0
        position_data = []

        for position, stock_info in zip(positions, results):
            if stock_info:
                current_value = stock_info['price'] * position['quantity']
                cost_basis = position['avg_cost'] * position['quantity']
                profit_loss = current_value - cost_basis
                profit_pct = (profit_loss / cost_basis) * 100

                total_value += current_value
                total_cost_basis += cost_basis

                position_data.append({
                    'symbol': position['symbol'],
                    'quantity': position['quantity'],
                    'avg_cost': position['avg_cost'],
                    'current_price': stock_info['price'],
                    'value': current_value,
                    'profit_loss': profit_loss,
                    'profit_pct': profit_pct
                })

        await loading_msg.delete()

        total_pl = total_value - paper_trading.STARTING_BALANCE
        total_pl_pct = (total_pl / paper_trading.STARTING_BALANCE) * 100

        embed = discord.Embed(
            title=f"📊 {target_user.name}'s Portfolio",
            description=f"💰 **Cash:** ${account['cash']:,.2f}\n📈 **Holdings:** ${total_value - account['cash']:,.2f}\n💼 **Total Value:** ${total_value:,.2f}",
            color=discord.Color.green() if total_pl >= 0 else discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        for pos in position_data[:10]:
            emoji = "🟢" if pos['profit_loss'] >= 0 else "🔴"
            sign = "+" if pos['profit_loss'] >= 0 else ""

            embed.add_field(
                name=f"{emoji} {pos['symbol']}",
                value=f"**{pos['quantity']} shares** @ ${pos['avg_cost']:,.2f}\n"
                      f"Current: ${pos['current_price']:,.2f}\n"
                      f"P/L: {sign}${pos['profit_loss']:,.2f} ({sign}{pos['profit_pct']:.2f}%)",
                inline=True
            )

        emoji = "🟢" if total_pl >= 0 else "🔴"
        sign = "+" if total_pl >= 0 else ""

        embed.set_footer(
            text=f"{emoji} Total P/L: {sign}${total_pl:,.2f} ({sign}{total_pl_pct:.2f}%)"
        )

        await ctx.send(embed=embed)

    @commands.command(name='transactions', aliases=['history', 'trades'])
    async def transactions(self, ctx, limit: int = 10):
        """
        View your recent transactions

        Usage: !transactions
        Usage: !transactions 20
        """
        if limit > 50:
            limit = 50

        transactions = await paper_trading.get_user_transactions(
            ctx.author.id,
            ctx.guild.id,
            limit
        )

        if not transactions:
            await ctx.send(f"No transaction history yet!\n\nUse `!buy <SYMBOL> <QUANTITY>` to start trading.")
            return

        embed = discord.Embed(
            title=f"📜 {ctx.author.name}'s Transaction History",
            description=f"Last {len(transactions)} transactions",
            color=config.BOT_COLOR
        )

        for txn in transactions:
            action_emoji = "🟢" if txn['action'] == "BUY" else "🔴"
            timestamp = txn['timestamp'].strftime("%m/%d %H:%M")

            embed.add_field(
                name=f"{action_emoji} {txn['action']} {txn['symbol']}",
                value=f"{txn['quantity']} shares @ ${txn['price']:,.2f}\nTotal: ${txn['total']:,.2f}\n{timestamp}",
                inline=True
            )

        await ctx.send(embed=embed)

    @commands.command(name='reset')
    async def reset(self, ctx):
        """
        Reset your paper trading account (warning: deletes all data!)

        Usage: !reset
        """
        embed = discord.Embed(
            title="⚠️ Reset Paper Trading Account?",
            description=f"This will:\n• Delete all your positions\n• Delete all transaction history\n• Reset cash to ${paper_trading.STARTING_BALANCE:,.2f}\n\nType `confirm` to proceed or `cancel` to abort.",
            color=discord.Color.orange()
        )

        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)

            if msg.content.lower() == 'confirm':
                success = await paper_trading.reset_account(ctx.author.id, ctx.guild.id)
                if success:
                    await ctx.send(f"✅ Account reset! You now have ${paper_trading.STARTING_BALANCE:,.2f} to trade with.")
                else:
                    await ctx.send("❌ Failed to reset account.")
            else:
                await ctx.send("❌ Reset cancelled.")

        except:
            await ctx.send("❌ Reset timed out.")

    @commands.command(name='leaderboard', aliases=['lb', 'rankings', 'top'])
    async def leaderboard(self, ctx, category: str = "value"):
        """
        View server leaderboard

        Usage: !leaderboard
        Usage: !leaderboard gainers
        Usage: !leaderboard volume

        Categories: value, gainers, volume
        """
        category = category.lower()

        if category not in ['value', 'gainers', 'volume']:
            await ctx.send(f"❌ Invalid category. Use: `value`, `gainers`, or `volume`")
            return

        accounts = await paper_trading.get_all_accounts(ctx.guild.id)

        if not accounts:
            await ctx.send("No traders yet! Use `!buy` to start trading and appear on the leaderboard.")
            return

        loading_msg = await ctx.send(f"⏳ Calculating leaderboard for {len(accounts)} traders...")

        import asyncio
        user_data = []

        for account in accounts:
            total_value = account['cash']
            positions = account.get('positions', [])

            if positions:
                symbols = [p['symbol'] for p in positions]
                tasks = [stock_api.get_stock_info(symbol) for symbol in symbols]
                results = await asyncio.gather(*tasks)

                for position, stock_info in zip(positions, results):
                    if stock_info:
                        total_value += stock_info['price'] * position['quantity']

            profit_loss = total_value - paper_trading.STARTING_BALANCE
            profit_pct = (profit_loss / paper_trading.STARTING_BALANCE) * 100

            if category == 'volume':
                txn_count = await paper_trading.get_user_transaction_count(
                    int(account['user_id']),
                    ctx.guild.id
                )
            else:
                txn_count = 0

            user_data.append({
                'user_id': account['user_id'],
                'total_value': total_value,
                'profit_loss': profit_loss,
                'profit_pct': profit_pct,
                'txn_count': txn_count
            })

        await loading_msg.delete()

        if category == 'value':
            user_data.sort(key=lambda x: x['total_value'], reverse=True)
            title = "🏆 Leaderboard - Total Portfolio Value"
            description = "Top traders by total portfolio value"
        elif category == 'gainers':
            user_data.sort(key=lambda x: x['profit_pct'], reverse=True)
            title = "📈 Leaderboard - Top Gainers"
            description = "Top traders by percentage gain"
        else:
            user_data.sort(key=lambda x: x['txn_count'], reverse=True)
            title = "🔥 Leaderboard - Most Active"
            description = "Top traders by number of transactions"

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )

        medals = ["🥇", "🥈", "🥉"]

        for i, user in enumerate(user_data[:10], 1):
            try:
                discord_user = await self.bot.fetch_user(int(user['user_id']))
                username = discord_user.name
            except:
                username = "Unknown User"

            if i <= 3:
                rank_display = medals[i - 1]
            else:
                rank_display = f"`#{i}`"

            if category == 'value':
                value_display = f"${user['total_value']:,.2f}"
                pl_emoji = "🟢" if user['profit_loss'] >= 0 else "🔴"
                pl_sign = "+" if user['profit_loss'] >= 0 else ""
                details = f"{pl_emoji} {pl_sign}${user['profit_loss']:,.2f} ({pl_sign}{user['profit_pct']:.2f}%)"
            elif category == 'gainers':
                pl_emoji = "🟢" if user['profit_pct'] >= 0 else "🔴"
                pl_sign = "+" if user['profit_pct'] >= 0 else ""
                value_display = f"{pl_emoji} {pl_sign}{user['profit_pct']:.2f}%"
                details = f"Value: ${user['total_value']:,.2f}"
            else:  # volume
                value_display = f"{user['txn_count']} trades"
                pl_emoji = "🟢" if user['profit_loss'] >= 0 else "🔴"
                pl_sign = "+" if user['profit_loss'] >= 0 else ""
                details = f"{pl_emoji} {pl_sign}{user['profit_pct']:.2f}% • ${user['total_value']:,.2f}"

            embed.add_field(
                name=f"{rank_display} {username}",
                value=f"**{value_display}**\n{details}",
                inline=True
            )

        embed.set_footer(text=f"Total traders: {len(accounts)} • Use !leaderboard <category> to switch")

        await ctx.send(embed=embed)


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(PaperTrading(bot))
