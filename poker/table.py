from typing import List, Optional
from poker.deck import Deck, Card
from poker.player import Player
from poker.hand import HandEvaluator


class Table:
    def __init__(self, chat_id: int, small_blind: int = 50, big_blind: int = 100):
        self.chat_id = chat_id
        self.small_blind = small_blind
        self.big_blind = big_blind

        self.players: List[Player] = []
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_index = 0
        self.current_player_index = 0
        self.round = "waiting"          # waiting, preflop, flop, turn, river, showdown
        self.status = "waiting"         # waiting, playing, finished

    def add_player(self, player: Player) -> bool:
        """O'yinchini stolga qo'shish"""
        if len(self.players) >= 10:
            return False
        if any(p.user_id == player.user_id for p in self.players):
            return False
        self.players.append(player)
        return True

    def remove_player(self, user_id: int) -> bool:
        """O'yinchini stoldan olib tashlash"""
        for i, p in enumerate(self.players):
            if p.user_id == user_id:
                self.players.pop(i)
                return True
        return False

    def get_player(self, user_id: int) -> Optional[Player]:
        for p in self.players:
            if p.user_id == user_id:
                return p
        return None

    def active_players(self) -> List[Player]:
        """Hali o'yinda qolgan o'yinchilar (fold qilmagan)"""
        return [p for p in self.players if p.status in ("active", "all-in")]

    def start_hand(self):
        """Yangi o'yinni boshlash"""
        if len(self.players) < 2:
            raise ValueError("Kamida 2 ta o'yinchi kerak")

        # Tozalash
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.round = "preflop"
        self.status = "playing"

        for p in self.players:
            p.reset_for_new_hand()

        # Dealer, Small Blind, Big Blind ni belgilash
        self._assign_positions()

        # Blindlarni qo'yish
        self._post_blinds()

        # Har bir o'yinchiga 2 tadan karta tarqatish
        for p in self.players:
            p.hole_cards = self.deck.deal(2)

        # Birinchi o'yinchini belgilash (Big Blind dan keyingi)
        self.current_player_index = (self.dealer_index + 3) % len(self.players)
        if len(self.players) == 2:  # Heads-up
            self.current_player_index = self.dealer_index

    def _assign_positions(self):
        """Dealer, SB, BB ni belgilash"""
        n = len(self.players)
        for p in self.players:
            p.is_dealer = p.is_small_blind = p.is_big_blind = False

        self.players[self.dealer_index].is_dealer = True
        sb_index = (self.dealer_index + 1) % n
        bb_index = (self.dealer_index + 2) % n
        self.players[sb_index].is_small_blind = True
        self.players[bb_index].is_big_blind = True

    def _post_blinds(self):
        """Small Blind va Big Blind ni avtomatik qo'yish"""
        for p in self.players:
            if p.is_small_blind:
                actual = p.place_bet(self.small_blind)
                self.pot += actual
            elif p.is_big_blind:
                actual = p.place_bet(self.big_blind)
                self.pot += actual
                self.current_bet = self.big_blind

    def next_round(self):
        """Keyingi raundga o'tish"""
        for p in self.players:
            p.reset_for_new_round()

        self.current_bet = 0

        if self.round == "preflop":
            self.community_cards = self.deck.deal(3)  # Flop
            self.round = "flop"
        elif self.round == "flop":
            self.community_cards += self.deck.deal(1)  # Turn
            self.round = "turn"
        elif self.round == "turn":
            self.community_cards += self.deck.deal(1)  # River
            self.round = "river"
        elif self.round == "river":
            self.round = "showdown"
            self.status = "finished"

    def get_winners(self) -> List[Player]:
        """G'oliblarni aniqlash"""
        contenders = [p for p in self.players if p.status != "folded"]

        if len(contenders) == 1:
            return contenders

        best_rank = -1
        best_kickers = []
        winners = []

        for p in contenders:
            all_cards = p.hole_cards + self.community_cards
            rank, kickers, _ = HandEvaluator.evaluate(all_cards)

            if rank > best_rank or (rank == best_rank and kickers > best_kickers):
                best_rank = rank
                best_kickers = kickers
                winners = [p]
            elif rank == best_rank and kickers == best_kickers:
                winners.append(p)

        return winners

    def move_dealer(self):
        """Keyingi o'yin uchun dealer tugmasini siljitish"""
        if self.players:
            self.dealer_index = (self.dealer_index + 1) % len(self.players)