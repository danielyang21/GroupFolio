"""
GroupFolio Discord Bot
Main entry point for the bot
"""
import discord
from discord.ext import commands
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

import config

# Set up intents (permissions for the bot)
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.guilds = True
#intents.members = True  # For future features

# Create bot instance
bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# MongoDB client (global access)
db_client = None
db = None


async def init_database():
    """Initialize MongoDB connection"""
    global db_client, db
    from utils import database

    if config.MONGODB_URI:
        try:
            db_client = AsyncIOMotorClient(config.MONGODB_URI)
            db = db_client[config.DATABASE_NAME]
            # Test the connection
            await db_client.admin.command('ping')

            # Set the database reference for utils/database.py to use
            database.set_db(db)

            print('✓ Connected to MongoDB!')
            return True
        except Exception as e:
            print(f'✗ MongoDB connection failed: {e}')
            print('Bot will continue without database functionality')
            return False
    else:
        print('⚠ No MongoDB URI found - database features disabled')
        return False


async def load_cogs():
    """Load all cog modules"""
    cogs_to_load = [
        'cogs.basic',
        'cogs.watchlist',
    ]

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f'✓ Loaded cog: {cog}')
        except Exception as e:
            print(f'✗ Failed to load cog {cog}: {e}')


@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord"""
    await init_database()

    print(f'\n{"="*50}')
    print(f'✓ {bot.user} has connected to Discord!')
    print(f'✓ Bot is in {len(bot.guilds)} server(s)')
    print(f'✓ Prefix: {config.COMMAND_PREFIX}')
    print(f'{"="*50}\n')


@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command not found. Use `{config.COMMAND_PREFIX}help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `{config.COMMAND_PREFIX}help {ctx.command}` for more info.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error in {ctx.command}: {error}")


async def main():
    """Main entry point"""
    async with bot:
        await load_cogs()
        if not config.DISCORD_TOKEN:
            print("Error: DISCORD_TOKEN not found in environment variables!")
            print("Please create a .env file with your bot token.")
            return
        await bot.start(config.DISCORD_TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
