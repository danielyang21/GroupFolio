"""Database utility functions for MongoDB operations"""

_db = None


def set_db(database):
    """Set the database instance (called by bot.py on startup)"""
    global _db
    _db = database


def get_db():
    """Get the database instance"""
    return _db


async def get_watchlist(guild_id):
    """Get the watchlist for a specific guild"""
    db = get_db()
    if db is None:
        return None

    return await db.watchlists.find_one({"guild_id": str(guild_id)})


async def add_stock_to_watchlist(guild_id, symbol, added_by_id, added_by_name):
    """Add a stock to the guild's watchlist"""
    db = get_db()
    if db is None:
        return (False, "database_not_connected")

    from datetime import datetime

    existing = await db.watchlists.find_one({
        "guild_id": str(guild_id),
        "stocks.symbol": symbol.upper()
    })

    if existing:
        return (False, "already_exists")

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
    """Remove a stock from the guild's watchlist"""
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
    """Get all stocks in a guild's watchlist"""
    watchlist = await get_watchlist(guild_id)
    if not watchlist:
        return []

    return watchlist.get("stocks", [])
