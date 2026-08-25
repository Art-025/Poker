from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from poker.table import Table
from poker.player import Player
from database.database import get_or_create_player

router = Router()

# Har bir guruh uchun stol saqlanadi
tables = {}


def get_join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🃏 JOIN POKER", callback_data="join_poker")]
    ])


@router.message(Command("poker"))
async def cmd_poker(message: Message):
    # Faqat guruhda ishlasin
    if message.chat.type == "private":
        await message.answer("❌ Bu buyruq faqat guruhda ishlaydi.\nBotni guruhga qo‘shing va u yerda /poker yozing.")
        return

    chat_id = message.chat.id

    # Agar stol allaqachon bo'lsa
    if chat_id in tables and tables[chat_id].status == "playing":
        await message.answer("⚠️ Hozir bu guruhda o'yin ketmoqda.")
        return

    # Yangi stol ochamiz
    table = Table(chat_id=chat_id)
    tables[chat_id] = table

    text = (
        "♠️ <b>KAGE POKER</b>\n"
        "Texas Hold'em\n\n"
        f"👥 Players: 0/10\n"
        f"💰 Buy-in: 1000 chips\n\n"
        "Qo‘shilish uchun pastdagi tugmani bosing."
    )

    await message.answer(text, reply_markup=get_join_keyboard())


@router.callback_query(F.data == "join_poker")
async def join_poker(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    if chat_id not in tables:
        await callback.answer("Stol topilmadi. /poker yozing.", show_alert=True)
        return

    table = tables[chat_id]

    if table.status == "playing":
        await callback.answer("O'yin allaqachon boshlangan.", show_alert=True)
        return

    # Foydalanuvchini bazadan olamiz
    db_player = await get_or_create_player(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    if db_player["balance"] < 1000:
        await callback.answer("❌ Sizda yetarli chip yo'q (kamida 1000 kerak).", show_alert=True)
        return

    # Player obyektini yaratamiz
    player = Player(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    player.chips = 1000  # Buy-in

    # Stolga qo'shamiz
    added = table.add_player(player)

    if not added:
        await callback.answer("Siz allaqachon stolga qo‘shilgansiz yoki stol to‘la.", show_alert=True)
        return

    # Xabarni yangilaymiz
    players_text = "\n".join([f"• {p.show_name()}" for p in table.players])
    text = (
        "♠️ <b>KAGE POKER</b>\n"
        "Texas Hold'em\n\n"
        f"👥 Players: {len(table.players)}/10\n"
        f"💰 Buy-in: 1000 chips\n\n"
        f"<b>O'yinchilar:</b>\n{players_text}\n\n"
        "Qo‘shilish uchun pastdagi tugmani bosing."
    )

    await callback.message.edit_text(text, reply_markup=get_join_keyboard())
    await callback.answer(f"{user.first_name} stolga qo‘shildi!")