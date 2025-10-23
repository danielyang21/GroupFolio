"""Paper trading utility functions"""
from datetime import datetime
from utils.database import get_db

STARTING_BALANCE = 100000.00


async def get_user_account(user_id, guild_id):
    """Get or create a user's paper trading account"""
    db = get_db()
    if db is None:
        return None

    account = await db.paper_accounts.find_one({
        "user_id": str(user_id),
        "guild_id": str(guild_id)
    })

    if not account:
        account = {
            "user_id": str(user_id),
            "guild_id": str(guild_id),
            "cash": STARTING_BALANCE,
            "positions": [],
            "created_at": datetime.utcnow()
        }
        await db.paper_accounts.insert_one(account)

    return account


async def buy_stock(user_id, guild_id, symbol, quantity, price):
    """Buy shares of a stock"""
    db = get_db()
    if db is None:
        return (False, "Database not connected")

    account = await get_user_account(user_id, guild_id)
    total_cost = price * quantity

    if account['cash'] < total_cost:
        return (False, f"Insufficient funds. Need ${total_cost:,.2f}, have ${account['cash']:,.2f}")

    positions = account.get('positions', [])
    existing_position = next((p for p in positions if p['symbol'] == symbol), None)

    if existing_position:
        old_value = existing_position['quantity'] * existing_position['avg_cost']
        new_value = old_value + total_cost
        new_quantity = existing_position['quantity'] + quantity
        new_avg_cost = new_value / new_quantity

        await db.paper_accounts.update_one(
            {
                "user_id": str(user_id),
                "guild_id": str(guild_id),
                "positions.symbol": symbol
            },
            {
                "$set": {
                    "positions.$.quantity": new_quantity,
                    "positions.$.avg_cost": new_avg_cost
                },
                "$inc": {"cash": -total_cost}
            }
        )
    else:
        new_position = {
            "symbol": symbol,
            "quantity": quantity,
            "avg_cost": price
        }
        await db.paper_accounts.update_one(
            {
                "user_id": str(user_id),
                "guild_id": str(guild_id)
            },
            {
                "$push": {"positions": new_position},
                "$inc": {"cash": -total_cost}
            }
        )

    await record_transaction(user_id, guild_id, "BUY", symbol, quantity, price)

    return (True, f"Bought {quantity} shares of {symbol} at ${price:,.2f}")


async def sell_stock(user_id, guild_id, symbol, quantity, price):
    """Sell shares of a stock"""
    db = get_db()
    if db is None:
        return (False, "Database not connected")

    account = await get_user_account(user_id, guild_id)
    positions = account.get('positions', [])
    position = next((p for p in positions if p['symbol'] == symbol), None)

    if not position:
        return (False, f"You don't own any {symbol}")

    if position['quantity'] < quantity:
        return (False, f"You only own {position['quantity']} shares of {symbol}")

    total_sale = price * quantity
    new_quantity = position['quantity'] - quantity

    if new_quantity == 0:
        await db.paper_accounts.update_one(
            {
                "user_id": str(user_id),
                "guild_id": str(guild_id)
            },
            {
                "$pull": {"positions": {"symbol": symbol}},
                "$inc": {"cash": total_sale}
            }
        )
    else:
        await db.paper_accounts.update_one(
            {
                "user_id": str(user_id),
                "guild_id": str(guild_id),
                "positions.symbol": symbol
            },
            {
                "$set": {"positions.$.quantity": new_quantity},
                "$inc": {"cash": total_sale}
            }
        )

    await record_transaction(user_id, guild_id, "SELL", symbol, quantity, price)

    cost_basis = position['avg_cost'] * quantity
    profit_loss = total_sale - cost_basis
    profit_pct = (profit_loss / cost_basis) * 100

    return (True, f"Sold {quantity} shares of {symbol} at ${price:,.2f}\nProfit/Loss: ${profit_loss:,.2f} ({profit_pct:+.2f}%)")


async def record_transaction(user_id, guild_id, action, symbol, quantity, price):
    """Record a transaction in history"""
    db = get_db()
    if db is None:
        return

    transaction = {
        "user_id": str(user_id),
        "guild_id": str(guild_id),
        "action": action,
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "total": price * quantity,
        "timestamp": datetime.utcnow()
    }

    await db.paper_transactions.insert_one(transaction)


async def get_user_transactions(user_id, guild_id, limit=10):
    """Get recent transactions for a user"""
    db = get_db()
    if db is None:
        return []

    cursor = db.paper_transactions.find({
        "user_id": str(user_id),
        "guild_id": str(guild_id)
    }).sort("timestamp", -1).limit(limit)

    return await cursor.to_list(length=limit)


async def reset_account(user_id, guild_id):
    """Reset a user's paper trading account"""
    db = get_db()
    if db is None:
        return False

    await db.paper_accounts.delete_one({
        "user_id": str(user_id),
        "guild_id": str(guild_id)
    })

    await db.paper_transactions.delete_many({
        "user_id": str(user_id),
        "guild_id": str(guild_id)
    })

    return True


async def get_all_accounts(guild_id):
    """Get all paper trading accounts for a guild"""
    db = get_db()
    if db is None:
        return []

    cursor = db.paper_accounts.find({"guild_id": str(guild_id)})
    return await cursor.to_list(length=None)


async def get_user_transaction_count(user_id, guild_id):
    """Get total number of transactions for a user"""
    db = get_db()
    if db is None:
        return 0

    count = await db.paper_transactions.count_documents({
        "user_id": str(user_id),
        "guild_id": str(guild_id)
    })

    return count
