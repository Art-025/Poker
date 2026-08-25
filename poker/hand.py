from typing import List, Tuple
from poker.deck import Card


class HandEvaluator:
    HAND_RANKS = {
        "High Card": 1,
        "One Pair": 2,
        "Two Pair": 3,
        "Three of a Kind": 4,
        "Straight": 5,
        "Flush": 6,
        "Full House": 7,
        "Four of a Kind": 8,
        "Straight Flush": 9,
        "Royal Flush": 10,
    }

    @staticmethod
    def evaluate(cards: List[Card]) -> Tuple[int, List[int], str]:
        """
        Kartalarni baholaydi.
        Qaytaradi: (rank_value, kickers, hand_name)
        """
        if len(cards) < 5:
            raise ValueError("Kamida 5 ta karta kerak")

        # Barcha mumkin bo'lgan 5-lik kombinatsiyalarni tekshiramiz
        from itertools import combinations

        best_rank = 0
        best_kickers = []
        best_name = "High Card"

        for combo in combinations(cards, 5):
            rank, kickers, name = HandEvaluator._evaluate_five(list(combo))
            if rank > best_rank or (rank == best_rank and kickers > best_kickers):
                best_rank = rank
                best_kickers = kickers
                best_name = name

        return best_rank, best_kickers, best_name

    @staticmethod
    def _evaluate_five(cards: List[Card]) -> Tuple[int, List[int], str]:
        values = sorted([c.value for c in cards], reverse=True)
        suits = [c.suit for c in cards]

        is_flush = len(set(suits)) == 1
        is_straight, straight_high = HandEvaluator._is_straight(values)

        # Royal Flush
        if is_flush and is_straight and straight_high == 14:
            return 10, [14], "Royal Flush"

        # Straight Flush
        if is_flush and is_straight:
            return 9, [straight_high], "Straight Flush"

        # Four of a Kind
        four = HandEvaluator._get_n_of_a_kind(values, 4)
        if four:
            kicker = [v for v in values if v != four[0]][0]
            return 8, [four[0], kicker], "Four of a Kind"

        # Full House
        three = HandEvaluator._get_n_of_a_kind(values, 3)
        pair = HandEvaluator._get_n_of_a_kind(values, 2)
        if three and pair:
            return 7, [three[0], pair[0]], "Full House"

        # Flush
        if is_flush:
            return 6, values, "Flush"

        # Straight
        if is_straight:
            return 5, [straight_high], "Straight"

        # Three of a Kind
        if three:
            kickers = [v for v in values if v != three[0]][:2]
            return 4, [three[0]] + kickers, "Three of a Kind"

        # Two Pair
        pairs = HandEvaluator._get_all_pairs(values)
        if len(pairs) >= 2:
            high_pair, low_pair = pairs[0], pairs[1]
            kicker = [v for v in values if v != high_pair and v != low_pair][0]
            return 3, [high_pair, low_pair, kicker], "Two Pair"

        # One Pair
        if pairs:
            kickers = [v for v in values if v != pairs[0]][:3]
            return 2, [pairs[0]] + kickers, "One Pair"

        # High Card
        return 1, values, "High Card"

    @staticmethod
    def _is_straight(values: List[int]) -> Tuple[bool, int]:
        unique = sorted(set(values), reverse=True)
        if len(unique) < 5:
            return False, 0

        # Oddiy straigh t
        for i in range(len(unique) - 4):
            if unique[i] - unique[i+4] == 4:
                return True, unique[i]

        # A-2-3-4-5 (wheel)
        if set([14, 2, 3, 4, 5]).issubset(set(values)):
            return True, 5

        return False, 0

    @staticmethod
    def _get_n_of_a_kind(values: List[int], n: int) -> List[int]:
        from collections import Counter
        counts = Counter(values)
        result = [v for v, cnt in counts.items() if cnt == n]
        return sorted(result, reverse=True)

    @staticmethod
    def _get_all_pairs(values: List[int]) -> List[int]:
        return HandEvaluator._get_n_of_a_kind(values, 2)