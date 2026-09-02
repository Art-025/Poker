from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from poker.player import Player
from poker.table import Table
from poker.betting import can_check, can_call, call_amount


def get_action_keyboard(player: Player, table: Table) -> InlineKeyboardMarkup:
    """O'yinchiga ko'rsatiladigan harakat tugmalari"""
    buttons = []

    # Fold har doim bor
    buttons.append([InlineKeyboardButton(text="❌ FOLD", callback_data="action_fold")])

    # Check yoki Call
    if can_check(player, table):
        buttons.append([InlineKeyboardButton(text="✅ CHECK", callback_data="action_check")])
    elif can_call(player, table):
        amount = call_amount(player, table)
        buttons.append([
            InlineKeyboardButton(
                text=f"📞 CALL {amount}",
                callback_data="action_call"
            )
        ])

    # Raise tugmalari
    min_raise = table.current_bet * 2 if table.current_bet > 0 else table.big_blind * 2
    raise_options = []

    if player.chips > call_amount(player, table):
        # 2x, 3x, Pot
        if min_raise <= player.chips + player.bet:
            raise_options.append(
                InlineKeyboardButton(text=f"⬆️ {min_raise}", callback_data=f"action_raise:{min_raise}")
            )
        pot_raise = table.pot + table.current_bet
        if pot_raise > min_raise and pot_raise <= player.chips + player.bet:
            raise_options.append(
                InlineKeyboardButton(text=f"🔥 POT {pot_raise}", callback_data=f"action_raise:{pot_raise}")
            )

    if raise_options:
        buttons.append(raise_options)

    # All-in
    if player.chips > 0:
        buttons.append([
            InlineKeyboardButton(
                text=f"💣 ALL-IN ({player.chips})",
                callback_data="action_allin"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_waiting_text(table: Table) -> str:
    """Joriy holatni ko'rsatuvchi matn"""
    current = table.get_current_player()
    current_name = current.show_name() if current else "—"

    community = " ".join(str(c) for c in table.community_cards) or "—"
    players_info = []
    for p in table.players:
        status_icon = {
            "active": "🟢",
            "folded": "🔴",
            "all-in": "🟡"
        }.get(p.status, "⚪")
        bet_info = f" (bet: {p.bet})" if p.bet > 0 else ""
        players_info.append(f"{status_icon} {p.show_name()} — {p.chips} 🪙{bet_info}")

    return (
        f"♠️ <b>KAGE POKER</b>\n"
        f"Raund: <b>{table.round_name.upper()}</b>\n"
        f"💰 Pot: <b>{table.pot}</b> 🪙\n"
        f"🃏 Stol: {community}\n\n"
        f"<b>O'yinchilar:</b>\n" + "\n".join(players_info) + "\n\n"
        f"👉 Hozir navbat: <b>{current_name}</b>"
    ) 