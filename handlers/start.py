from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from database.database import get_or_create_player

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user

    player = await get_or_create_player(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    text = (
        f"👋 Salom, <b>{user.full_name}</b>!\n\n"
        f"🃏 <b>KAGE POKER</b>ga xush kelibsiz!\n\n"
        f"💰 Sizning balansingiz: <b>{player['balance']:,}</b> 🪙\n\n"
        f"Buyruqlar:\n"
        f"/profile - Profilingiz\n"
        f"/poker - Poker o'yinini boshlash\n"
        f"/help - Yordam"
    )

    await message.answer(text)