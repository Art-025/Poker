from typing import List, Optional
from poker.table import Table
from poker.player import Player
from poker.betting import do_fold, do_check, do_call, do_raise, do_all_in
from poker.evaluator import evaluate_hand, hand_name


def process_action(table: Table, player: Player, action: str, raise_amount: int = 0) -> str:
    """
    O'yinchining harakatini bajaradi.
    Qaytaradi: natija matni
    """
    if player.status != "active":
        return "Siz allaqachon harakat qilgansiz yoki fold qilgansiz."

    if action == "fold":
        do_fold(player)
        return f"{player.show_name()} fold qildi."

    elif action == "check":
        if do_check(player, table):
            return f"{player.show_name()} check qildi."
        return "Check qilib bo'lmaydi."

    elif action == "call":
        amount = do_call(player, table)
        return f"{player.show_name()} call qildi ({amount} 🪙)."

    elif action == "raise":
        amount = do_raise(player, table, raise_amount)
        if amount == 0:
            return "Raise qilib bo'lmadi."
        return f"{player.show_name()} raise qildi → {raise_amount} 🪙."

    elif action == "allin":
        amount = do_all_in(player, table)
        return f"{player.show_name()} ALL-IN qildi ({amount} 🪙)!"

    return "Noma'lum harakat."


def is_betting_round_over(table: Table) -> bool:
    """Betting raundi tugaganmi?"""
    active = table.players_who_can_act()
    if len(active) == 0:
        return True

    # Barcha active o'yinchilar bir xil stavka qo'yganmi?
    for p in active:
        if p.bet != table.current_bet:
            return False
    return True


def advance_round(table: Table) -> str:
    """
    Keyingi raundga o'tadi (flop / turn / river / showdown)
    Qaytaradi: nima bo'lganini aytuvchi matn
    """
    # Har bir o'yinchining joriy stavkasini nolga tushiramiz
    for p in table.players:
        p.reset_for_new_round()

    table.current_bet = 0

    if table.round_name == "preflop":
        # Flop — 3 karta
        table.community_cards = table.deck.deal(3)
        table.round_name = "flop"
        return "🃏 FLOP ochildi!"

    elif table.round_name == "flop":
        # Turn — 1 karta
        table.community_cards += table.deck.deal(1)
        table.round_name = "turn"
        return "🃏 TURN ochildi!"

    elif table.round_name == "turn":
        # River — 1 karta
        table.community_cards += table.deck.deal(1)
        table.round_name = "river"
        return "🃏 RIVER ochildi!"

    elif table.round_name == "river":
        table.round_name = "showdown"
        return "🏁 SHOWDOWN!"

    return ""


def determine_winners(table: Table) -> List[Player]:
    """Eng kuchli qo'lga ega o'yinchilarni topadi"""
    contenders = [p for p in table.players if p.status in ("active", "all-in")]
    if not contenders:
        return []

    best_score = (-1, [])
    winners = []

    for p in contenders:
        score = evaluate_hand(p.hole_cards, table.community_cards)
        if score > best_score:
            best_score = score
            winners = [p]
        elif score == best_score:
            winners.append(p)

    return winners


def finish_hand(table: Table) -> str:
    """O'yinni yakunlaydi va potni tarqatadi"""
    winners = determine_winners(table)

    if not winners:
        table.status = "finished"
        return "G'olib topilmadi."

    # Potni bo'lish
    share = table.pot // len(winners)
    remainder = table.pot % len(winners)

    result_lines = []
    for i, winner in enumerate(winners):
        amount = share + (1 if i < remainder else 0)
        winner.chips += amount
        score = evaluate_hand(winner.hole_cards, table.community_cards)
        result_lines.append(
            f"🏆 {winner.show_name()} — {hand_name(score[0])} (+{amount} 🪙)"
        )

    table.pot = 0
    table.status = "finished"

    # Keyingi o'yin uchun dealer siljiydi
    table.dealer_index = (table.dealer_index + 1) % len(table.players)

    return "\n".join(result_lines) 