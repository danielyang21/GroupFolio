import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX', '!')
MONGODB_URI = os.getenv('MONGODB_URI')

# MongoDB client (will be initialized when bot starts)
db_client = None
db = None

# Set up intents (permissions for the bot)
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

# Create bot instance
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord"""
    global db_client, db

    # Initialize MongoDB connection
    if MONGODB_URI:
        try:
            db_client = AsyncIOMotorClient(MONGODB_URI)
            db = db_client.groupfolio  # Database name
            # Test the connection
            await db_client.admin.command('ping')
            print('✓ Connected to MongoDB!')
        except Exception as e:
            print(f'✗ MongoDB connection failed: {e}')
            print('Bot will continue without database functionality')
    else:
        print('⚠ No MongoDB URI found - database features disabled')

    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} server(s)')


@bot.command(name='ping')
async def ping(ctx):
    """Simple ping command to test if bot is responding"""
    latency = round(bot.latency * 1000)  # Convert to milliseconds
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')


@bot.command(name='hello')
async def hello(ctx):
    """Greet the user"""
    await ctx.send(f'Hello {ctx.author.mention}! Welcome to GroupFolio!')


@bot.command(name='info')
async def info(ctx):
    """Display bot information"""
    embed = discord.Embed(
        title="GroupFolio Bot",
        description="A Discord bot for sharing and tracking stock portfolios",
        color=discord.Color.blue()
    )
    embed.add_field(name="Prefix", value=PREFIX, inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)

    # Show database status
    db_status = "✓ Connected" if db else "✗ Not connected"
    embed.add_field(name="Database", value=db_status, inline=True)

    embed.set_footer(text="More features coming soon!")

    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    """Handle errors gracefully"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command not found. Use `{PREFIX}help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `{PREFIX}help {ctx.command}` for more info.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error: {error}")


if __name__ == '__main__':
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
    else:
        bot.run(TOKEN)
