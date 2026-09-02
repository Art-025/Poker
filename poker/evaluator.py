from collections import Counter
from typing import List, Tuple
from poker.deck import Card


def evaluate_hand(hole_cards: List[Card], community_cards: List[Card]) -> Tuple[int, list]:
    """
    Eng yaxshi 5 kartani topadi va kuchini qaytaradi.
    Qaytadi: (rank, [values...])
    rank:
        8 = Straight Flush
        7 = Four of a Kind
        6 = Full House
        5 = Flush
        4 = Straight
        3 = Three of a Kind
        2 = Two Pair
        1 = One Pair
        0 = High Card
    """
    all_cards = hole_cards + community_cards
    if len(all_cards) < 5:
        # Hali yetarli karta yo'q (preflop/flop)
        ranks = sorted([c.value for c in hole_cards], reverse=True)
        return (0, ranks)

    best = (0, [])

    # Barcha 5 kartalik kombinatsiyalarni tekshirish
    from itertools import combinations
    for combo in combinations(all_cards, 5):
        score = _score_five_cards(list(combo))
        if score > best:
            best = score

    return best


def _score_five_cards(cards: List[Card]) -> Tuple[int, list]:
    ranks = sorted([c.value for c in cards], reverse=True)
    suits = [c.suit for c in cards]
    rank_counts = Counter(ranks)
    counts = sorted(rank_counts.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = _is_straight(ranks)

    # Straight Flush
    if is_straight and is_flush:
        return (8, [max(ranks)])

    # Four of a Kind
    if counts == [4, 1]:
        four = [r for r, c in rank_counts.items() if c == 4][0]
        kicker = [r for r, c in rank_counts.items() if c == 1][0]
        return (7, [four, kicker])

    # Full House
    if counts == [3, 2]:
        three = [r for r, c in rank_counts.items() if c == 3][0]
        pair = [r for r, c in rank_counts.items() if c == 2][0]
        return (6, [three, pair])

    # Flush
    if is_flush:
        return (5, ranks)

    # Straight
    if is_straight:
        return (4, [max(ranks) if ranks != [14, 5, 4, 3, 2] else 5])

    # Three of a Kind
    if counts == [3, 1, 1]:
        three = [r for r, c in rank_counts.items() if c == 3][0]
        kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
        return (3, [three] + kickers)

    # Two Pair
    if counts == [2, 2, 1]:
        pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
        kicker = [r for r, c in rank_counts.items() if c == 1][0]
        return (2, pairs + [kicker])

    # One Pair
    if counts == [2, 1, 1, 1]:
        pair = [r for r, c in rank_counts.items() if c == 2][0]
        kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
        return (1, [pair] + kickers)

    # High Card
    return (0, ranks)


def _is_straight(ranks: List[int]) -> bool:
    ranks = sorted(set(ranks), reverse=True)
    if len(ranks) < 5:
        return False
    # Oddiy straight
    for i in range(len(ranks) - 4):
        if ranks[i] - ranks[i+4] == 4:
            return True
    # A-2-3-4-5 (wheel)
    if set([14, 2, 3, 4, 5]).issubset(set(ranks)):
        return True
    return False


def hand_name(rank: int) -> str:
    names = {
        8: "Straight Flush",
        7: "Four of a Kind",
        6: "Full House",
        5: "Flush",
        4: "Straight",
        3: "Three of a Kind",
        2: "Two Pair",
        1: "One Pair",
        0: "High Card"
    }
    return names.get(rank, "Unknown") 