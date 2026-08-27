from __future__ import annotations

import logging

from aiogram import Bot, Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import ADMIN_ID

router = Router()

logger = logging.getLogger(__name__)


def build_group_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """
    Create confirmation buttons for a newly added group.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Roziman",
                    callback_data=f"group_accept:{chat_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etaman",
                    callback_data=f"group_reject:{chat_id}",
                ),
            ]
        ]
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> IS_MEMBER
    )
)
async def bot_added_to_group(
    event: ChatMemberUpdated,
    bot: Bot,
) -> None:
    """
    Runs whenever the bot becomes a member of a group.

    IMPORTANT:
    This does NOT check who added the bot.
    Even if the owner/admin personally adds the bot,
    the notification is still sent.
    """

    chat = event.chat
    user = event.from_user

    group_name = chat.title or "Noma'lum guruh"
    group_id = chat.id

    if user:
        username = (
            f"@{user.username}"
            if user.username
            else user.full_name
        )
        user_id = user.id
    else:
        username = "Noma'lum foydalanuvchi"
        user_id = "Noma'lum"

    text = (
        "🤖 <b>KAGE POKER guruhga qo‘shildi!</b>\n\n"
        f"📌 <b>Guruh:</b> {group_name}\n"
        f"🆔 <b>Guruh ID:</b> <code>{group_id}</code>\n\n"
        f"👤 <b>Qo‘shgan foydalanuvchi:</b> {username}\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
        "Bot ushbu guruhga qo‘shildi."
    )

    keyboard = build_group_keyboard(group_id)

    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            reply_markup=keyboard,
        )

        logger.info(
            "Bot added to group: chat_id=%s, title=%s, added_by=%s",
            group_id,
            group_name,
            user_id,
        )

    except Exception:
        logger.exception(
            "Failed to notify ADMIN_ID=%s about new group %s",
            ADMIN_ID,
            group_id,
        )


@router.callback_query(
    lambda callback: callback.data
    and callback.data.startswith("group_accept:")
)
async def accept_group(
    callback: CallbackQuery,
) -> None:
    """
    Handle the 'Roziman' button.
    """

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "❌ Bu tugmadan faqat bot administratori foydalanishi mumkin.",
            show_alert=True,
        )
        return

    try:
        chat_id = int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await callback.answer(
            "❌ Guruh ID noto‘g‘ri.",
            show_alert=True,
        )
        return

    await callback.answer("✅ Guruh tasdiqlandi.")

    try:
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            "✅ <b>Guruh tasdiqlandi.</b>\n"
            f"🆔 <code>{chat_id}</code>"
        )
    except Exception:
        logger.exception("Failed to edit accepted group message.")


@router.callback_query(
    lambda callback: callback.data
    and callback.data.startswith("group_reject:")
)
async def reject_group(
    callback: CallbackQuery,
    bot: Bot,
) -> None:
    """
    Handle the 'Rad etaman' button.

    Currently this only records the rejection in the admin message.
    The actual group-leave logic can be added later.
    """

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "❌ Bu tugmadan faqat bot administratori foydalanishi mumkin.",
            show_alert=True,
        )
        return

    try:
        chat_id = int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await callback.answer(
            "❌ Guruh ID noto‘g‘ri.",
            show_alert=True,
        )
        return

    await callback.answer("❌ Guruh rad etildi.")

    try:
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            "❌ <b>Guruh rad etildi.</b>\n"
            f"🆔 <code>{chat_id}</code>"
        )
    except Exception:
        logger.exception("Failed to edit rejected group message.")