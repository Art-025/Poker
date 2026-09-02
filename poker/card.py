 class Card:
    SUITS = {
        "h": "♥️",
        "d": "♦️",
        "c": "♣️",
        "s": "♠️"
    }
    RANKS = {
        2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
        7: "7", 8: "8", 9: "9", 10: "10",
        11: "J", 12: "Q", 13: "K", 14: "A"
    }

    def __init__(self, rank: int, suit: str):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.RANKS[self.rank]}{self.SUITS[self.suit]}"

    def __repr__(self):
        return self.__str__()