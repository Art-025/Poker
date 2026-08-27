from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "♠️ <b>KAGE POKER</b> ga xush kelibsiz!\n\n"
        "Texas Hold'em poker o'yini.\n"
        "Faqat virtual chip. Real pul yo'q.\n\n"
        "Buyruqlar:\n"
        "/poker — O'yinni boshlash (guruhda)\n"
        "/profile — Profilingiz\n"
        "/rules — Qoidalar\n"
        "/help — Yordam\n"
        "/id — ID ni ko'rish"
    )
    await message.answer(text)


@router.message(Command("id"))
async def cmd_id(message: Message):
    text = (
        f"👤 <b>Sizning ID:</b> <code>{message.from_user.id}</code>\n"
        f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>\n"
        f"📌 <b>Chat turi:</b> {message.chat.type}"
    )
    if message.chat.title:
        text += f"\n🏷 <b>Guruh nomi:</b> {message.chat.title}"
    await message.answer(text)