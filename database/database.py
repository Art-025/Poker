import aiosqlite
from config import START_CHIPS

DB_PATH = "kage_poker.db"


async def init_database():
    """Bazani yaratish va jadvallarni tayyorlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Players jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Transactions jadvali (chip harakatlari uchun)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER,
                to_user_id INTEGER,
                amount INTEGER,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    """Foydalanuvchini olish yoki yangi yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
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