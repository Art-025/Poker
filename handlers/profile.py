from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.database import get_or_create_player

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = message.from_user

    player = await get_or_create_player(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    text = (
        f"👤 <b>Profil</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Ism: {user.full_name}\n"
        f"💰 Balans: <b>{player['balance']:,}</b> 🪙\n"
        f"🎮 O'yinlar: {player['games_played']}\n"
        f"🏆 G'alabalar: {player['games_won']}"
    )

    await message.answer(text)