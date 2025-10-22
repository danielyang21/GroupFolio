"""
Paper trading utility functions
"""
from datetime import datetime
from utils.database import get_db

# Starting balance for new users
STARTING_BALANCE = 100000.00


async def get_user_account(user_id, guild_id):
    """
    Get or create a user's paper trading account

    Args:
        user_id (int): Discord user ID
        guild_id (int): Discord guild ID

    Returns:
        dict: User account with cash balance and positions
    """
    db = get_db()
    if db is None:
        return None

    account = await db.paper_accounts.find_one({
        "user_id": str(user_id),
        "guild_id": str(guild_id)
    })

    if not account:
        # Create new account with starting balance
        account = {
            "user_id": str(user_id),
            "guild_id": str(guild_id),
            "cash": STARTING_BALANCE,
            "positions": [],  # List of holdings
            "created_at": datetime.utcnow()
        }
        await db.paper_accounts.insert_one(account)

    return account


async def buy_stock(user_id, guild_id, symbol, quantity, price):
    """
    Buy shares of a stock

    Args:
        user_id (int): Discord user ID
        guild_id (int): Discord guild ID
        symbol (str): Stock symbol
        quantity (int): Number of shares to buy
        price (float): Current price per share

    Returns:
        tuple: (success: bool, message: str)
    """
    db = get_db()
    if db is None:
        return (False, "Database not connected")

    account = await get_user_account(user_id, guild_id)
    total_cost = price * quantity

    # Check if user has enough cash
    if account['cash'] < total_cost:
        return (False, f"Insufficient funds. Need ${total_cost:,.2f}, have ${account['cash']:,.2f}")

    # Update or add position
    positions = account.get('positions', [])
    existing_position = next((p for p in positions if p['symbol'] == symbol), None)

    if existing_position:
        # Update existing position (calculate new average cost)
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
        # Add new position
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

    # Record transaction
    await record_transaction(user_id, guild_id, "BUY", symbol, quantity, price)

    return (True, f"Bought {quantity} shares of {symbol} at ${price:,.2f}")


async def sell_stock(user_id, guild_id, symbol, quantity, price):
    """
    Sell shares of a stock

    Args:
        user_id (int): Discord user ID
        guild_id (int): Discord guild ID
        symbol (str): Stock symbol
        quantity (int): Number of shares to sell
        price (float): Current price per share

    Returns:
        tuple: (success: bool, message: str)
    """
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

    # Update position
    new_quantity = position['quantity'] - quantity

    if new_quantity == 0:
        # Remove position entirely
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
        # Update quantity
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

    # Record transaction
    await record_transaction(user_id, guild_id, "SELL", symbol, quantity, price)

    # Calculate profit/loss
    cost_basis = position['avg_cost'] * quantity
    profit_loss = total_sale - cost_basis
    profit_pct = (profit_loss / cost_basis) * 100

    return (True, f"Sold {quantity} shares of {symbol} at ${price:,.2f}\nProfit/Loss: ${profit_loss:,.2f} ({profit_pct:+.2f}%)")


async def record_transaction(user_id, guild_id, action, symbol, quantity, price):
    """
    Record a transaction in history

    Args:
        user_id (int): Discord user ID
        guild_id (int): Discord guild ID
        action (str): "BUY" or "SELL"
        symbol (str): Stock symbol
        quantity (int): Number of shares
        price (float): Price per share
    """
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
    """
    Get recent transactions for a user

    Args:
        user_id (int): Discord user ID
        guild_id (int): Discord guild ID
        limit (int): Number of transactions to return

    Returns:
        list: Recent transactions
    """
    db = get_db()
    if db is None:
        return []

    cursor = db.paper_transactions.find({
        "user_id": str(user_id),
        "guild_id": str(guild_id)
    }).sort("timestamp", -1).limit(limit)

    return await cursor.to_list(length=limit)


async def reset_account(user_id, guild_id):
    """
    Reset a user's paper trading account

    Args:
        user_id (int): Discord user ID
        guild_id (int): Discord guild ID

    Returns:
        bool: Success
    """
    db = get_db()
    if db is None:
        return False

    # Delete account and transactions
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
    """
    Get all paper trading accounts for a guild

    Args:
        guild_id (int): Discord guild ID

    Returns:
        list: All accounts in the guild
    """
    db = get_db()
    if db is None:
        return []

    cursor = db.paper_accounts.find({"guild_id": str(guild_id)})
    return await cursor.to_list(length=None)


async def get_user_transaction_count(user_id, guild_id):
    """
    Get total number of transactions for a user

    Args:
        user_id (int): Discord user ID
        guild_id (int): Discord guild ID

    Returns:
        int: Number of transactions
    """
    db = get_db()
    if db is None:
        return 0

    count = await db.paper_transactions.count_documents({
        "user_id": str(user_id),
        "guild_id": str(guild_id)
    })

    return count
