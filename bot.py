import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.database import init_database
from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.transfer import router as transfer_router

# Logging
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Routerlarni ulash
dp.include_router(start_router)
dp.include_router(profile_router)
dp.include_router(transfer_router)


async def main():
    await init_database()
    
    print("KAGE POKER bot ishga tushmoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")