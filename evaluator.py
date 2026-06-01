"""Five-card hand evaluator used to rank Texas Hold'em showdowns."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from itertools import combinations

from cards import Card


class HandCategory(IntEnum):
    # TODO: Task 1 - define the hand categories in order from lowest to highest
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9


@dataclass(frozen=True, order=True)
class HandRank:
    # TODO: Task 2 - define the HandRank dataclass with the category and tiebreakers
    category: HandCategory
    tiebreakers: tuple
    # TODO: Task 2 - return a version of the category
    def category_name(self) -> str:
        return self.category.name
    


class HandEvaluator:
    # TODO: Task 3 - implement the best_rank method to evaluate the best possible hand from a list of cards
    def best_rank(self, cards: list[Card]) -> HandRank:
        if len(cards) < 5:
            raise ValueError("not enough cards in the deck")
        ranks_of_fives = []
        for five_cards in combinations(cards, 5):
            ranks_of_fives.append(self._rank_five(five_cards))
        return max(ranks_of_fives)


    def _rank_five(self, cards: list[Card]) -> HandRank:
        # TODO: Task 4 - implement the logic to rank a five-card hand according to poker rules
        ranks = [card.rank.value for card in cards]
        counts = Counter(ranks)
        groups = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
        is_flush = all(card.suit.value == cards[0].suit.value for card in cards)
        straight_high = self._straight_high(ranks)

        # TODO: Task 6 - implement the ranking logic
        # NOTE: this is a hard task - ranking logic implemented in problem #6
        if is_flush and straight_high:
            return HandRank(HandCategory.STRAIGHT_FLUSH, (straight_high,))
        if groups[0][1] == 4:
            return HandRank(HandCategory.FOUR_OF_A_KIND, (groups[0][0], groups[1][0]))
        if groups[0][1] == 3 and groups[1][1] == 2:
            return HandRank(HandCategory.FULL_HOUSE, (groups[0][0], groups[1][0]))
        if is_flush:
            return HandRank(HandCategory.FLUSH, tuple(sorted(ranks, reverse=True)))
        if straight_high:
            return HandRank(HandCategory.STRAIGHT, (straight_high,))
        if groups[0][1] == 3:
            return HandRank(HandCategory.THREE_OF_A_KIND, (groups[0][0], groups[1][0], groups[2][0]))
        if groups[0][1] == 2 and groups[1][1] == 2:
            return HandRank(HandCategory.TWO_PAIR, (groups[0][0], groups[1][0], groups[2][0]))
        if groups[0][1] == 2:
            return HandRank(HandCategory.ONE_PAIR, (groups[0][0], groups[1][0], groups[2][0], groups[3][0]))

        return HandRank(HandCategory.HIGH_CARD, (groups[0][0], groups[1][0], groups[2][0], groups[3][0], groups[4][0])) 


    def _straight_high(self, ranks: list[int]) -> int | None:
        # TODO: Task 5 - implement the logic to determine if the hand contains a straight, 
        # and if so, return the high card of the straight
        sorted_ranks = sorted(ranks)
        if sorted_ranks == [2, 3, 4, 5, 14]:
            return 5
        for i in range (len(ranks) - 1):
            if sorted_ranks[i+1] - sorted_ranks[i] != 1:
                return None
    
        return sorted_ranks[4]

