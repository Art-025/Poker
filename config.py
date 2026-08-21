import os
from dotenv import load_dotenv

load_dotenv()

# Bot token (Telegram BotFather dan olinadi)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin ID (o'zingizning Telegram ID raqamingiz)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Boshlang'ich chip miqdori
START_CHIPS = 10000

# Poker sozlamalari
MIN_PLAYERS = 2
MAX_PLAYERS = 10
BUY_IN = 1000