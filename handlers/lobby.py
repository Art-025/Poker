import asyncio
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from poker.table import Table
from poker.player import Player
from database.database import get_or_create_player
from database.database import is_group_approved, get_or_create_player

router = Router()

# chat_id -> Table
tables = {}

# chat_id -> lobby message_id (timer uchun)
lobby_messages = {}

LOBBY_TIME = 60  # soniya
MIN_PLAYERS = 2
BUY_IN = 1000


def get_lobby_keyboard(players_count: int):
    buttons = [
        [InlineKeyboardButton(text="🃏 JOIN POKER", callback_data="join_poker")]
    ]
    if players_count >= MIN_PLAYERS:
        buttons.append(
            [InlineKeyboardButton(text="🚀 START GAME", callback_data="start_game")]
        )
    buttons.append(
        [InlineKeyboardButton(text="❌ BEKOR QILISH", callback_data="cancel_lobby")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lobby_text(table: Table, seconds_left: int = None):
    players_text = "\n".join([f"• {p.show_name()}" for p in table.players]) or "—"
    timer = f"\n⏱ Qolgan vaqt: <b>{seconds_left}</b> soniya" if seconds_left is not None else ""

    return (
        "♠️ <b>KAGE POKER LOBBY</b>\n"
        "Texas Hold'em\n\n"
        f"👥 Players: <b>{len(table.players)}</b>/10\n"
        f"💰 Buy-in: {BUY_IN} chips\n"
        f"{timer}\n\n"
        f"<b>O'yinchilar:</b>\n{players_text}\n\n"
        f"Kamida {MIN_PLAYERS} kishi bo'lganda START bosish mumkin.\n"
        "Vaqt tugasa stol avtomatik yopiladi."
    )
@router.message(Command("poker"))
async def cmd_poker(message: Message):
    if message.chat.type == "private":
        await message.answer("❌ Bu buyruq faqat guruhda ishlaydi.")
        return

    chat_id = message.chat.id

    # === RUXSAT TEKSHIRUVI ===
    if not await is_group_approved(chat_id):
        await message.answer(
            "🚫 <b>Ruxsat berilmagan!</b>\n\n"
            "Bu guruhda botdan foydalanish uchun egadan ruxsat olish kerak.\n"
            "Ruxsat so‘rash uchun botni guruhga qayta qo‘shing yoki egaga murojaat qiling."
        )
        return
    # ========================

    # Agar o'yin ketayotgan bo'lsa
    if chat_id in tables and tables[chat_id].status == "playing":
        await message.answer("⚠️ Hozir bu guruhda o'yin ketmoqda. Tugashini kuting.")
        return

    # Agar lobby ochiq bo'lsa
    if chat_id in tables and tables[chat_id].status == "waiting":
        table = tables[chat_id]
        
        # Agar o'yinchi yo'q bo'lsa — eski lobbyni o'chiramiz
        if len(table.players) == 0:
            tables.pop(chat_id, None)
            lobby_messages.pop(chat_id, None)
        else:
            players_count = len(table.players)
            await message.answer(
                f"ℹ️ Lobby allaqachon ochiq.\n"
                f"Hozir {players_count} ta o'yinchi bor.\n\n"
                f"JOIN tugmasini bosing yoki ❌ BEKOR QILISH ni bosing."
            )
            return

    # Yangi lobby ochish
    table = Table(chat_id=chat_id)
    table.status = "waiting"
    table.created_at = datetime.now()
    tables[chat_id] = table

    msg = await message.answer(
        get_lobby_text(table, LOBBY_TIME),
        reply_markup=get_lobby_keyboard(0)
    )
    lobby_messages[chat_id] = msg.message_id

    asyncio.create_task(lobby_timer(chat_id, message.bot))


@router.callback_query(F.data == "join_poker")
async def join_poker(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    if chat_id not in tables:
        await callback.answer("Lobby yopilgan. /poker yozing.", show_alert=True)
        return

    table = tables[chat_id]

    if table.status != "waiting":
        await callback.answer("O'yin allaqachon boshlangan yoki tugagan.", show_alert=True)
        return

    # Allaqachon qo'shilganmi?
    if table.get_player(user.id):
        await callback.answer("Siz allaqachon stolga qo'shilgansiz.", show_alert=True)
        return

    db_player = await get_or_create_player(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    if db_player["balance"] < BUY_IN:
        await callback.answer(
            f"❌ Yetarli chip yo'q (kamida {BUY_IN} kerak).\nSizda: {db_player['balance']} 🪙",
            show_alert=True
        )
        return

    # Database dan chip olamiz
    from database.database import update_balance
    new_balance = db_player["balance"] - BUY_IN
    await update_balance(user.id, new_balance)

    player = Player(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    player.chips = BUY_IN

    table.add_player(player)

    # Qolgan vaqtni hisoblash
    elapsed = (datetime.now() - table.created_at).seconds
    seconds_left = max(0, LOBBY_TIME - elapsed)

    await callback.message.edit_text(
        get_lobby_text(table, seconds_left),
        reply_markup=get_lobby_keyboard(len(table.players))
    )
    await callback.answer(f"{user.first_name} qo'shildi!")

@router.callback_query(F.data == "cancel_lobby")
async def cancel_lobby(callback: CallbackQuery):
    chat_id = callback.message.chat.id

    if chat_id not in tables:
        await callback.answer("Lobby topilmadi.", show_alert=True)
        return

    table = tables[chat_id]
    if table.status != "waiting":
        await callback.answer("O'yin boshlangan, bekor qilib bo'lmaydi.", show_alert=True)
        return

    tables.pop(chat_id, None)
    lobby_messages.pop(chat_id, None)

    await callback.message.edit_text("❌ Lobby bekor qilindi.\n\nYana ochish uchun /poker yozing.")
    await callback.answer("Lobby yopildi.")

@router.callback_query(F.data == "start_game")
async def start_game(callback: CallbackQuery):
    chat_id = callback.message.chat.id

    if chat_id not in tables:
        await callback.answer("Lobby topilmadi.", show_alert=True)
        return

    table = tables[chat_id]

    if table.status != "waiting":
        await callback.answer("O'yin allaqachon boshlangan.", show_alert=True)
        return

    if len(table.players) < MIN_PLAYERS:
        await callback.answer(f"Kamida {MIN_PLAYERS} ta o'yinchi kerak.", show_alert=True)
        return

    # O'yinni boshlash
    try:
        table.start_hand()
    except Exception as e:
        await callback.answer(f"Xato: {e}", show_alert=True)
        return

    # Kartalarni private yuborish
    for p in table.players:
        cards_text = " ".join(str(card) for card in p.hole_cards)
        try:
            await callback.bot.send_message(
                chat_id=p.user_id,
                text=f"🔒 <b>Sizning kartalaringiz:</b>\n\n{cards_text}"
            )
        except Exception:
            await callback.message.answer(
                f"⚠️ {p.show_name()} ga karta yuborib bo'lmadi.\n"
                f"U botga private chatda /start bosishi kerak."
            )

    # Birinchi o'yinchiga tugmalar bilan xabar
    from poker.actions import get_action_keyboard, get_waiting_text

    current = table.get_current_player()
    text = get_waiting_text(table)

    if current:
        kb = get_action_keyboard(current, table)
        await callback.message.edit_text(text, reply_markup=kb)
    else:
        await callback.message.edit_text(text)

    await callback.answer("O'yin boshlandi!")

@router.callback_query(F.data == "cancel_game")
async def cancel_game(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    if chat_id not in tables:
        await callback.answer("O'yin topilmadi.", show_alert=True)
        return

    table = tables[chat_id]

    # Faqat o'yin ketayotganda
    if table.status != "playing":
        await callback.answer("Hozir o'yin ketmayapti.", show_alert=True)
        return

    # Faqat o'yindagi o'yinchilar yoki admin bekor qila oladi
    player = table.get_player(user_id)
    if not player and user_id != 1100194757:
        await callback.answer("Faqat o'yindagi o'yinchilar bekor qila oladi.", show_alert=True)
        return

    # O'yinni yopish
    tables.pop(chat_id, None)
    lobby_messages.pop(chat_id, None)

    await callback.message.edit_text(
        "❌ <b>O'yin bekor qilindi.</b>\n\n"
        "Yangi o'yin boshlash uchun /poker yozing."
    )
    await callback.answer("O'yin bekor qilindi.")

# O'yinni bekor qilish
    buttons.append([
        InlineKeyboardButton(text="🚫 O'YINNI BEKOR QILISH", callback_data="cancel_game")
    ])

 