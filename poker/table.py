from typing import List, Optional
from poker.player import Player
from poker.deck import Deck


class Table:
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.players: List[Player] = []
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.status = "waiting"  # waiting, playing, finished
        self.dealer_index = 0
        self.current_player_index = 0
        self.small_blind = 50
        self.big_blind = 100
        self.round_name = "preflop"  # preflop, flop, turn, river, showdown
        self.created_at = None

    def add_player(self, player: Player) -> bool:
        if len(self.players) >= 10:
            return False
        if self.get_player(player.user_id):
            return False
        self.players.append(player)
        return True

    def get_player(self, user_id: int) -> Optional[Player]:
        for p in self.players:
            if p.user_id == user_id:
                return p
        return None

    def remove_player(self, user_id: int):
        self.players = [p for p in self.players if p.user_id != user_id]

    def active_players(self) -> List[Player]:
        return [p for p in self.players if p.status in ("active", "all-in")]

    def players_who_can_act(self) -> List[Player]:
        return [p for p in self.players if p.status == "active"]

    def start_hand(self):
        """Yangi qo'lni boshlash"""
        if len(self.players) < 2:
            raise ValueError("Kamida 2 ta o'yinchi kerak")

        self.status = "playing"
        self.pot = 0
        self.current_bet = 0
        self.community_cards = []
        self.round_name = "preflop"
        self.deck.reset()

        # Har bir o'yinchini tozalash
        for p in self.players:
            p.reset_for_new_hand()

        # Dealer belgilash
        self.dealer_index = self.dealer_index % len(self.players)
        self.players[self.dealer_index].is_dealer = True

        # Small Blind va Big Blind
        sb_index = (self.dealer_index + 1) % len(self.players)
        bb_index = (self.dealer_index + 2) % len(self.players)

        sb_player = self.players[sb_index]
        bb_player = self.players[bb_index]

        sb_player.is_small_blind = True
        bb_player.is_big_blind = True

        # Blindlarni olish
        sb_amount = sb_player.place_bet(self.small_blind)
        bb_amount = bb_player.place_bet(self.big_blind)

        self.pot += sb_amount + bb_amount
        self.current_bet = self.big_blind

        # Kartalarni tarqatish (har biriga 2 tadan)
        for p in self.players:
            p.hole_cards = self.deck.deal(2)

        # Birinchi harakat qiluvchi (Big Blind dan keyingi)
        self.current_player_index = (bb_index + 1) % len(self.players)

    def next_player(self):
        """Keyingi harakat qila oladigan o'yinchiga o'tish"""
        n = len(self.players)
        for _ in range(n):
            self.current_player_index = (self.current_player_index + 1) % n
            player = self.players[self.current_player_index]
            if player.status == "active":
                return player
        return None

    def get_current_player(self) -> Optional[Player]:
        if not self.players:
            return None
        return self.players[self.current_player_index]