import random
from typing import List


class Card:
    SUITS = ["♠", "♥", "♦", "♣"]
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    RANK_VALUES = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
        "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14
    }

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
        self.value = self.RANK_VALUES[rank]

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return self.__str__()


class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.reset()

    def reset(self):
        """Kolodani qayta yaratish va aralashtirish"""
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num: int = 1) -> List[Card]:
        """Berilgan miqdordagi kartani tarqatish"""
        if num > len(self.cards):
            raise ValueError("Kolodada yetarli karta yo'q")
        dealt = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt

    def remaining(self) -> int:
        return len(self.cards)