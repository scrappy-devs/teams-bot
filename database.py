# database.py
import aiosqlite
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path("teams_bot.db")

async def init_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER NOT NULL,
                    game TEXT NOT NULL,
                    wins INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, game)
                )
            """)
            await db.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def update_match_result(user_id: int, game: str, won: bool):
    """Update wins or losses for a user in a specific game.
    
    Args:
        user_id: Discord user ID
        game: Game code (e.g., "mpt", "cod")
        won: True if user won, False if user lost
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            if won:
                # Insert or update wins
                await db.execute("""
                    INSERT INTO user_stats (user_id, game, wins, losses)
                    VALUES (?, ?, 1, 0)
                    ON CONFLICT(user_id, game) DO UPDATE SET
                        wins = wins + 1
                """, (user_id, game.lower()))
            else:
                # Insert or update losses
                await db.execute("""
                    INSERT INTO user_stats (user_id, game, wins, losses)
                    VALUES (?, ?, 0, 1)
                    ON CONFLICT(user_id, game) DO UPDATE SET
                        losses = losses + 1
                """, (user_id, game.lower()))
            await db.commit()
    except Exception as e:
        logger.error(f"Error updating match result for user {user_id}, game {game}: {e}")
        # Don't raise - we don't want database errors to crash the bot

async def get_user_stats(user_id: int, game: str = None):
    """Get user statistics.
    
    Args:
        user_id: Discord user ID
        game: Optional game code. If None, returns stats for all games.
    
    Returns:
        If game is specified: dict with 'wins' and 'losses' or None if no record exists
        If game is None: list of dicts with 'game', 'wins', 'losses' for all games
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            if game:
                async with db.execute("""
                    SELECT wins, losses FROM user_stats
                    WHERE user_id = ? AND game = ?
                """, (user_id, game.lower())) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return {"wins": row[0], "losses": row[1]}
                    return None
            else:
                async with db.execute("""
                    SELECT game, wins, losses FROM user_stats
                    WHERE user_id = ?
                    ORDER BY game
                """, (user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [{"game": row[0], "wins": row[1], "losses": row[2]} for row in rows]
    except Exception as e:
        logger.error(f"Error getting user stats for user {user_id}, game {game}: {e}")
        return None if game else []

async def get_users_stats_for_matchmaking(users, game: str):
    """Get stats for multiple users for matchmaking purposes.
    
    Args:
        users: List of Discord user objects
        game: Game code (e.g., "mpt", "cod")
    
    Returns:
        List of tuples: (user, wins, losses) where wins/losses default to 0 if user not in DB
    """
    if not users:
        return []
    
    try:
        user_ids = [user.id for user in users]
        placeholders = ','.join('?' * len(user_ids))
        
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"""
                SELECT user_id, wins, losses FROM user_stats
                WHERE user_id IN ({placeholders}) AND game = ?
            """, (*user_ids, game.lower())) as cursor:
                rows = await cursor.fetchall()
                # Create a dict mapping user_id to (wins, losses)
                stats_dict = {row[0]: (row[1], row[2]) for row in rows}
        
        # Return list with stats (default to 0, 0 if not found)
        result = []
        for user in users:
            wins, losses = stats_dict.get(user.id, (0, 0))
            result.append((user, wins, losses))
        
        return result
    except Exception as e:
        logger.error(f"Error getting users stats for matchmaking: {e}")
        # Return default stats if error occurs
        return [(user, 0, 0) for user in users]
