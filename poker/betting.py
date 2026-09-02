 from typing import Optional
from poker.player import Player
from poker.table import Table


def can_check(player: Player, table: Table) -> bool:
    """Check qilish mumkinmi?"""
    return player.bet >= table.current_bet and player.status == "active"


def can_call(player: Player, table: Table) -> bool:
    """Call qilish mumkinmi?"""
    return player.bet < table.current_bet and player.status == "active" and player.chips > 0


def call_amount(player: Player, table: Table) -> int:
    """Call qilish uchun kerakli miqdor"""
    return max(0, table.current_bet - player.bet)


def do_fold(player: Player):
    player.fold()


def do_check(player: Player, table: Table) -> bool:
    if not can_check(player, table):
        return False
    return True


def do_call(player: Player, table: Table) -> int:
    """Call qiladi, qancha qo‘yganini qaytaradi"""
    amount = call_amount(player, table)
    if amount <= 0:
        return 0
    actual = player.place_bet(amount)
    table.pot += actual
    return actual


def do_raise(player: Player, table: Table, raise_to: int) -> int:
    """
    raise_to — umumiy stavka (masalan current_bet 100 bo‘lsa, raise_to=300)
    """
    if raise_to <= table.current_bet:
        return 0

    needed = raise_to - player.bet
    if needed > player.chips:
        # All-in
        actual = player.place_bet(player.chips)
        table.pot += actual
        table.current_bet = max(table.current_bet, player.bet)
        return actual

    actual = player.place_bet(needed)
    table.pot += actual
    table.current_bet = raise_to
    return actual


def do_all_in(player: Player, table: Table) -> int:
    """Butun chipni qo‘yadi"""
    amount = player.chips
    actual = player.place_bet(amount)
    table.pot += actual
    if player.bet > table.current_bet:
        table.current_bet = player.bet
    return actual