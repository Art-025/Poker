from aiogram import Router, F, Bot
from aiogram.types import ChatMemberUpdated, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, IS_ADMIN

from database.database import is_group_approved, approve_group, remove_group
from config import ADMIN_ID

router = Router()

OWNER_ID = 1100194757  # Sizning ID


@router.my_chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER)
)
async def bot_added_to_group(event: ChatMemberUpdated, bot: Bot):
    """Bot yangi guruhga qo'shilganda"""
    chat = event.chat

    # Agar allaqachon ruxsat berilgan bo'lsa
    if await is_group_approved(chat.id):
        return

    # Egaga xabar yuboramiz
    text = (
        "🔔 <b>Yangi guruhga qo'shildim!</b>\n\n"
        f"📌 Guruh: <b>{chat.title}</b>\n"
        f"🆔 Chat ID: <code>{chat.id}</code>\n\n"
        "Bu guruhda ishlashga ruxsat berasizmi?"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Roziman", callback_data=f"approve_group:{chat.id}:{chat.title or 'No title'}"),
            InlineKeyboardButton(text="❌ Rad etaman", callback_data=f"reject_group:{chat.id}")
        ]
    ])

    try:
        await bot.send_message(OWNER_ID, text, reply_markup=keyboard)
    except Exception:
        pass  # Egaga yozib bo'lmasa


@router.callback_query(F.data.startswith("approve_group:"))
async def approve_group_callback(callback: CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Sizda ruxsat yo'q.", show_alert=True)
        return

    parts = callback.data.split(":", 2)
    chat_id = int(parts[1])
    title = parts[2] if len(parts) > 2 else "Unknown"

    await approve_group(chat_id, title, OWNER_ID)

    await callback.message.edit_text(
        f"✅ <b>Ruxsat berildi!</b>\n\n"
        f"Guruh: <b>{title}</b>\n"
        f"Chat ID: <code>{chat_id}</code>\n\n"
        "Endi bot bu guruhda ishlaydi."
    )
    await callback.answer("Guruh tasdiqlandi!")


@router.callback_query(F.data.startswith("reject_group:"))
async def reject_group_callback(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Sizda ruxsat yo'q.", show_alert=True)
        return

    chat_id = int(callback.data.split(":")[1])

    await remove_group(chat_id)

    # Ixtiyoriy: botni guruhdan chiqarib yuborish
    try:
        await bot.leave_chat(chat_id)
    except Exception:
        pass

    await callback.message.edit_text(
        f"❌ <b>Rad etildi.</b>\n\n"
        f"Chat ID: <code>{chat_id}</code>\n"
        "Bot guruhdan chiqarildi."
    )
    await callback.answer("Guruh rad etildi.")