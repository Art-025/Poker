from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from database.database import get_or_create_player
import aiosqlite
from config import START_CHIPS

router = Router()
DB_PATH = "kage_poker.db"


@router.message(Command("send"))
async def cmd_send(message: Message):
    """
    Ishlatish: /send <user_id> <miqdor>
    Masalan: /send 123456789 500
    """
    args = message.text.split()

    if len(args) != 3:
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "To'g'ri ishlatish:\n"
            "<code>/send user_id miqdor</code>\n\n"
            "Masalan:\n"
            "<code>/send 123456789 1000</code>"
        )
        return

    try:
        to_user_id = int(args[1])
        amount = int(args[2])
    except ValueError:
        await message.answer("❌ user_id va miqdor raqam bo'lishi kerak!")
        return

    if amount <= 0:
        await message.answer("❌ Miqdor 0 dan katta bo'lishi kerak!")
        return

    from_user = message.from_user

    if from_user.id == to_user_id:
        await message.answer("❌ O'zingizga chip yubora olmaysiz!")
        return

    # Jo'natuvchini olish
    sender = await get_or_create_player(
        user_id=from_user.id,
        username=from_user.username,
        full_name=from_user.full_name
    )

    if sender["balance"] < amount:
        await message.answer(
            f"❌ Yetarli chip yo'q!\n"
            f"Sizning balansingiz: <b>{sender['balance']:,}</b> 🪙"
        )
        return

    # Qabul qiluvchini olish (agar yo'q bo'lsa yaratiladi)
    receiver = await get_or_create_player(user_id=to_user_id)

    # Chip o'tkazish
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE players SET balance = balance - ? WHERE user_id = ?",
            (amount, from_user.id)
        )
        await db.execute(
            "UPDATE players SET balance = balance + ? WHERE user_id = ?",
            (amount, to_user_id)
        )
        await db.execute(
            "INSERT INTO transactions (from_user_id, to_user_id, amount, reason) VALUES (?, ?, ?, ?)",
            (from_user.id, to_user_id, amount, "transfer")
        )
        await db.commit()

    await message.answer(
        f"✅ Muvaffaqiyatli o'tkazildi!\n\n"
        f"💸 <b>{amount:,}</b> 🪙 yuborildi\n"
        f"👤 Qabul qiluvchi ID: <code>{to_user_id}</code>"
    )