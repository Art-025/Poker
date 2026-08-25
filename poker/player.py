from typing import List, Optional
from poker.deck import Card


class Player:
    def __init__(self, user_id: int, username: str = None, full_name: str = None):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name or str(user_id)

        # Stolga tegishli
        self.chips = 0              # Stolga olib kirgan chip
        self.hole_cards: List[Card] = []  # 2 ta yashirin karta
        self.bet = 0                # Joriy raunddagi stavka
        self.total_bet = 0          # Butun o'yin davomidagi jami stavka
        self.status = "active"      # active / folded / all-in / sitting_out

        # Pozitsiya
        self.is_dealer = False
        self.is_small_blind = False
        self.is_big_blind = False

    def add_chips(self, amount: int):
        self.chips += amount

    def remove_chips(self, amount: int) -> int:
        """Chip olib tashlash. Yetarli bo'lmasa, qolganini oladi (all-in)."""
        actual = min(amount, self.chips)
        self.chips -= actual
        return actual

    def place_bet(self, amount: int) -> int:
        """Stavka qo'yish"""
        actual = self.remove_chips(amount)
        self.bet += actual
        self.total_bet += actual

        if self.chips == 0:
            self.status = "all-in"

        return actual

    def fold(self):
        self.status = "folded"
        self.hole_cards = []

    def reset_for_new_round(self):
        """Yangi raund uchun tozalash (flop, turn, river oldidan)"""
        self.bet = 0

    def reset_for_new_hand(self):
        """Yangi o'yin (hand) uchun tozalash"""
        self.hole_cards = []
        self.bet = 0
        self.total_bet = 0
        self.status = "active"
        self.is_dealer = False
        self.is_small_blind = False
        self.is_big_blind = False

    def show_name(self) -> str:
        """Guruhda ko'rsatish uchun ism"""
        if self.username:
            return f"@{self.username}"
        return self.full_name

    def __str__(self):
        return f"{self.show_name()} ({self.chips} 🪙)"