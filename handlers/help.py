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
        "/profile — Profilingiz va balans\n"
        "/poker — Poker stolini ochish (guruhda)\n"
        "/rules — Poker qoidalari va tushuntirish\n"
        "/help — Shu yordam xabari\n"
        "/send — Chip yuborish\n\n"
        "<b>Chip yuborish:</b>\n"
        "<code>/send user_id miqdor</code>\n"
        "Masalan: <code>/send 123456789 1000</code>\n\n"
        "<b>Poker qanday o'ynaladi:</b>\n"
        "1. Guruhda /poker yozing\n"
        "2. Do'stlaringiz JOIN bosing\n"
        "3. START GAME bosing\n"
        "4. Kartalar private chatga keladi\n"
        "5. O'ynang!\n\n"
        "💰 Faqat virtual chip. Real pul yo'q."
    )
    await message.answer(text)