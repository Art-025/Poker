from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.lobby import tables
from poker.game_engine import process_action, is_betting_round_over, advance_round, finish_hand
from poker.actions import get_action_keyboard, get_waiting_text

router = Router()


@router.callback_query(F.data.startswith("action_"))
async def handle_action(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    if chat_id not in tables:
        await callback.answer("O'yin topilmadi.", show_alert=True)
        return

    table = tables[chat_id]

    if table.status != "playing":
        await callback.answer("O'yin hozir ketmayapti.", show_alert=True)
        return

    player = table.get_player(user_id)
    if not player:
        await callback.answer("Siz bu o'yinda emassiz.", show_alert=True)
        return

    current = table.get_current_player()
    if not current or current.user_id != user_id:
        await callback.answer("Hozir sizning navbatingiz emas!", show_alert=True)
        return

    # Harakatni aniqlash
    data = callback.data
    action = data.replace("action_", "")
    raise_amount = 0

    if action.startswith("raise:"):
        raise_amount = int(action.split(":")[1])
        action = "raise"

    # Harakatni bajarish
    result = process_action(table, player, action, raise_amount)

    # Navbatni keyingi o'yinchiga o'tkazish
    table.next_player()

    # Betting raundi tugadimi?
    if is_betting_round_over(table):
        if table.round_name == "river":
            # Showdown
            winners_text = finish_hand(table)
            text = (
                f"🏁 <b>SHOWDOWN!</b>\n\n"
                f"{get_waiting_text(table)}\n\n"
                f"<b>Natija:</b>\n{winners_text}"
            )
            await callback.message.edit_text(text)
            tables.pop(chat_id, None)
            await callback.answer("O'yin tugadi!")
            return
        else:
            # Keyingi raund (Flop / Turn / River)
            advance_round(table)
            # Birinchi harakat qiluvchini belgilash
            table.current_player_index = table.dealer_index
            table.next_player()

    # Yangi holatni ko'rsatish
    current = table.get_current_player()
    text = get_waiting_text(table)

    if current and table.status == "playing":
        kb = get_action_keyboard(current, table)
        await callback.message.edit_text(text, reply_markup=kb)
    else:
        await callback.message.edit_text(text)

    await callback.answer(result)