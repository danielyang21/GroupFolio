"""
Basic commands cog - ping, hello, info
"""
import discord
from discord.ext import commands
import config


class Basic(commands.Cog):
    """Basic bot commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'🏓 Pong! Latency: {latency}ms')

    @commands.command(name='hello')
    async def hello(self, ctx):
        """Greet the user"""
        await ctx.send(f'Hello {ctx.author.mention}! Welcome to GroupFolio!')

    @commands.command(name='info')
    async def info(self, ctx):
        """Display bot information"""
        # Import here to avoid circular dependency
        import bot as bot_module

        embed = discord.Embed(
            title="GroupFolio Bot",
            description="A Discord bot for group stock watchlists and portfolio tracking",
            color=config.BOT_COLOR
        )
        embed.add_field(name="Prefix", value=config.COMMAND_PREFIX, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)

        # Show database status
        db_status = "✓ Connected" if bot_module.db else "✗ Not connected"
        embed.add_field(name="Database", value=db_status, inline=True)

        embed.add_field(
            name="Commands",
            value=f"`{config.COMMAND_PREFIX}help` - Show all commands\n"
                  f"`{config.COMMAND_PREFIX}watchlist` - View group watchlist\n"
                  f"`{config.COMMAND_PREFIX}addstock` - Add stock to watchlist",
            inline=False
        )

        embed.set_footer(text="GroupFolio - Track stocks together!")

        await ctx.send(embed=embed)


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(Basic(bot))
