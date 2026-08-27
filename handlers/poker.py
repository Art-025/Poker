from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from poker.table import Table
from poker.player import Player
from database.database import get_or_create_player

router = Router()

# Har bir guruh uchun stol
tables = {}


def get_lobby_keyboard(players_count: int):
    buttons = [
        [InlineKeyboardButton(text="🃏 JOIN POKER", callback_data="join_poker")]
    ]
    if players_count >= 2:
        buttons.append(
            [InlineKeyboardButton(text="🚀 START GAME", callback_data="start_game")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("poker"))
async def cmd_poker(message: Message):
    if message.chat.type == "private":
        await message.answer("❌ Bu buyruq faqat guruhda ishlaydi.")
        return

    chat_id = message.chat.id

    if chat_id in tables and tables[chat_id].status == "playing":
        await message.answer("⚠️ Hozir bu guruhda o'yin ketmoqda.")
        return

    table = Table(chat_id=chat_id)
    tables[chat_id] = table

    text = (
        "♠️ <b>KAGE POKER</b>\n"
        "Texas Hold'em\n\n"
        f"👥 Players: 0/10\n"
        f"💰 Buy-in: 1000 chips\n\n"
        "Qo‘shilish uchun tugmani bosing."
    )

    await message.answer(text, reply_markup=get_lobby_keyboard(0))


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

    db_player = await get_or_create_player(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    if db_player["balance"] < 1000:
        await callback.answer("❌ Yetarli chip yo'q (kamida 1000 kerak).", show_alert=True)
        return

    player = Player(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    player.chips = 1000

    added = table.add_player(player)
    if not added:
        await callback.answer("Siz allaqachon stolga qo‘shilgansiz yoki stol to‘la.", show_alert=True)
        return

    players_text = "\n".join([f"• {p.show_name()}" for p in table.players])
    text = (
        "♠️ <b>KAGE POKER</b>\n"
        "Texas Hold'em\n\n"
        f"👥 Players: {len(table.players)}/10\n"
        f"💰 Buy-in: 1000 chips\n\n"
        f"<b>O'yinchilar:</b>\n{players_text}\n\n"
        "Qo‘shilish uchun tugmani bosing."
    )

    await callback.message.edit_text(text, reply_markup=get_lobby_keyboard(len(table.players)))
    await callback.answer(f"{user.first_name} qo‘shildi!")


@router.callback_query(F.data == "start_game")
async def start_game(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    if chat_id not in tables:
        await callback.answer("Stol topilmadi.", show_alert=True)
        return

    table = tables[chat_id]

    if table.status == "playing":
        await callback.answer("O'yin allaqachon boshlangan.", show_alert=True)
        return

    if len(table.players) < 2:
        await callback.answer("Kamida 2 ta o'yinchi kerak.", show_alert=True)
        return

    try:
        table.start_hand()
    except Exception as e:
        await callback.answer(f"Xato: {e}", show_alert=True)
        return

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

    players_text = "\n".join([f"• {p.show_name()} — {p.chips} 🪙" for p in table.players])
    text = (
        "🚀 <b>O'YIN BOSHLANDI!</b>\n\n"
        f"💰 Pot: {table.pot} 🪙\n"
        f"🃏 Raund: Pre-flop\n\n"
        f"<b>O'yinchilar:</b>\n{players_text}\n\n"
        "Kartalar private chatga yuborildi."
    )

    await callback.message.edit_text(text)
    await callback.answer("O'yin boshlandi!")

    # Keyingi o'yinchiga o'tish
    move_to_next_player(table)

    # Agar raund tugagan bo'lsa — keyingi street
    if is_betting_round_complete(table):
        table.next_round()
        if table.round == "showdown":
            await do_showdown(callback.message, table)
            return
        # Yangi raund boshida current_bet = 0, birinchi active o'yinchidan boshlash
        table.current_bet = 0
        for p in table.players:
            p.reset_for_new_round()
        table.current_player_index = find_first_active(table)

    await show_table_state(callback.message, table)


def move_to_next_player(table: Table):
    n = len(table.players)
    for _ in range(n):
        table.current_player_index = (table.current_player_index + 1) % n
        p = table.players[table.current_player_index]
        if p.status == "active":
            return


def find_first_active(table: Table) -> int:
    for i, p in enumerate(table.players):
        if p.status == "active":
            return i
    return 0


def is_betting_round_complete(table: Table) -> bool:
    active = [p for p in table.players if p.status == "active"]
    if len(active) <= 1:
        return True
    return all(p.bet == table.current_bet for p in active)


async def do_showdown(message: Message, table: Table):
    winners = table.get_winners()
    if not winners:
        text = "O'yin tugadi. G'olib topilmadi."
    else:
        win_amount = table.pot // len(winners)
        names = ", ".join(w.show_name() for w in winners)
        for w in winners:
            w.chips += win_amount
        text = (
            f"🏆 <b>SHOWDOWN</b>\n\n"
            f"G'olib: {names}\n"
            f"Yutgan summa: {win_amount} 🪙 (har biriga)\n"
            f"Jami pot: {table.pot}"
        )

    table.status = "finished"
    await message.edit_text(text)
