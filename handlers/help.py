from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "🃏 <b>KAGE POKER — Yordam</b>\n\n"
        "<b>Asosiy buyruqlar:</b>\n"
        "/start — Botni ishga tushirish\n"
        "/profile — Profilingizni ko‘rish\n"
        "/send — Chip yuborish\n"
        "/help — Shu yordam xabari\n\n"
        "<b>Chip yuborish:</b>\n"
        "<code>/send user_id miqdor</code>\n"
        "Masalan: <code>/send 123456789 1000</code>\n\n"
        "Tez orada:\n"
        "• Poker o‘yini\n"
        "• Shop\n"
        "• Kartalar / Waifu\n"
        "• Turnirlar"
    )
    await message.answer(text)