import aiosqlite

DB_PATH = "poker.db"
START_CHIPS = 10000


async def init_database():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance INTEGER DEFAULT 10000,
                games_played INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS approved_groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                approved_by INTEGER,
                approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    print("Database tayyor!")


async def get_or_create_player(user_id: int, username: str = None, full_name: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, full_name, balance, games_played, games_won FROM players WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            player = await cursor.fetchone()

        if player is None:
            await db.execute(
                "INSERT INTO players (user_id, username, full_name, balance) VALUES (?, ?, ?, ?)",
                (user_id, username, full_name, START_CHIPS)
            )
            await db.commit()
            return {
                "user_id": user_id,
                "username": username,
                "full_name": full_name,
                "balance": START_CHIPS,
                "games_played": 0,
                "games_won": 0
            }

        return {
            "user_id": player[0],
            "username": player[1],
            "full_name": player[2],
            "balance": player[3],
            "games_played": player[4],
            "games_won": player[5]
        }


async def is_group_approved(chat_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM approved_groups WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None


async def approve_group(chat_id: int, title: str, approved_by: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO approved_groups (chat_id, title, approved_by) VALUES (?, ?, ?)",
            (chat_id, title, approved_by)
        )
        await db.commit()


async def remove_group(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM approved_groups WHERE chat_id = ?", (chat_id,)
        )
        await db.commit()

async def update_balance(user_id: int, new_balance: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE players SET balance = ? WHERE user_id = ?",
            (new_balance, user_id)
        )
        await db.commit()


async def add_game_result(user_id: int, won: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        if won:
            await db.execute(
                "UPDATE players SET games_played = games_played + 1, games_won = games_won + 1 WHERE user_id = ?",
                (user_id,)
            )
        else:
            await db.execute(
                "UPDATE players SET games_played = games_played + 1 WHERE user_id = ?",
                (user_id,)
            )
        await db.commit()