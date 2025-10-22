"""
Database utility functions for MongoDB operations
"""

# Global database reference (set by bot on startup)
_db = None


def set_db(database):
    """Set the database instance (called by bot.py on startup)"""
    global _db
    _db = database


def get_db():
    """Get the database instance"""
    return _db


async def get_watchlist(guild_id):
    """
    Get the watchlist for a specific guild

    Args:
        guild_id (int): Discord guild (server) ID

    Returns:
        dict: Watchlist document or None if not found
    """
    db = get_db()
    if db is None:
        return None

    return await db.watchlists.find_one({"guild_id": str(guild_id)})


async def add_stock_to_watchlist(guild_id, symbol, added_by_id, added_by_name):
    """
    Add a stock to the guild's watchlist

    Args:
        guild_id (int): Discord guild ID
        symbol (str): Stock symbol (e.g., 'AAPL')
        added_by_id (int): Discord user ID who added it
        added_by_name (str): Discord username

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    db = get_db()
    if db is None:
        return (False, "database_not_connected")

    from datetime import datetime

    # Check if stock already exists in watchlist
    existing = await db.watchlists.find_one({
        "guild_id": str(guild_id),
        "stocks.symbol": symbol.upper()
    })

    if existing:
        return (False, "already_exists")

    # Add stock to watchlist (or create watchlist if it doesn't exist)
    result = await db.watchlists.update_one(
        {"guild_id": str(guild_id)},
        {
            "$push": {
                "stocks": {
                    "symbol": symbol.upper(),
                    "added_by_id": str(added_by_id),
                    "added_by_name": added_by_name,
                    "added_at": datetime.utcnow()
                }
            }
        },
        upsert=True
    )

    return (result.acknowledged, None)


async def remove_stock_from_watchlist(guild_id, symbol):
    """
    Remove a stock from the guild's watchlist

    Args:
        guild_id (int): Discord guild ID
        symbol (str): Stock symbol to remove

    Returns:
        bool: True if successful, False otherwise
    """
    db = get_db()
    if db is None:
        return False

    result = await db.watchlists.update_one(
        {"guild_id": str(guild_id)},
        {
            "$pull": {
                "stocks": {"symbol": symbol.upper()}
            }
        }
    )

    return result.modified_count > 0


async def get_watchlist_stocks(guild_id):
    """
    Get all stocks in a guild's watchlist

    Args:
        guild_id (int): Discord guild ID

    Returns:
        list: List of stock dictionaries
    """
    watchlist = await get_watchlist(guild_id)
    if not watchlist:
        return []

    return watchlist.get("stocks", [])
