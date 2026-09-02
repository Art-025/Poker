from typing import Optional
from poker.player import Player
from poker.table import Table


def can_check(player: Player, table: Table) -> bool:
    return player.bet >= table.current_bet and player.status == "active"


def can_call(player: Player, table: Table) -> bool:
    return player.bet < table.current_bet and player.status == "active" and player.chips > 0


def call_amount(player: Player, table: Table) -> int:
    return max(0, table.current_bet - player.bet)


def do_fold(player: Player):
    player.fold()


def do_check(player: Player, table: Table) -> bool:
    if not can_check(player, table):
        return False
    return True


def do_call(player: Player, table: Table) -> int:
    amount = call_amount(player, table)
    if amount <= 0:
        return 0
    actual = player.place_bet(amount)
    table.pot += actual
    return actual


def do_raise(player: Player, table: Table, raise_to: int) -> int:
    if raise_to <= table.current_bet:
        return 0

    needed = raise_to - player.bet
    if needed > player.chips:
        actual = player.place_bet(player.chips)
        table.pot += actual
        table.current_bet = max(table.current_bet, player.bet)
        return actual

    actual = player.place_bet(needed)
    table.pot += actual
    table.current_bet = raise_to
    return actual


def do_all_in(player: Player, table: Table) -> int:
    amount = player.chips
    actual = player.place_bet(amount)
    table.pot += actual
    if player.bet > table.current_bet:
        table.current_bet = player.bet
    return actual