"""
Configuration management for GroupFolio bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = 'groupfolio'

# SnapTrade Configuration (for future use)
SNAPTRADE_CONSUMER_KEY = os.getenv('SNAPTRADE_CONSUMER_KEY')
SNAPTRADE_CONSUMER_SECRET = os.getenv('SNAPTRADE_CONSUMER_SECRET')

# Stock API Configuration
# Using Alpha Vantage (free tier: 25 requests/day)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')

# Bot Configuration
BOT_COLOR = 0x3498db  # Blue color for embeds
