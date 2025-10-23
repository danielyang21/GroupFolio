"""Configuration management for GroupFolio bot"""
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = 'groupfolio'

SNAPTRADE_CONSUMER_KEY = os.getenv('SNAPTRADE_CONSUMER_KEY')
SNAPTRADE_CONSUMER_SECRET = os.getenv('SNAPTRADE_CONSUMER_SECRET')

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')

BOT_COLOR = 0x3498db
