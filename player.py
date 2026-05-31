"""Player model for the poker table."""

from __future__ import annotations

from dataclasses import dataclass, field

from cards import Card


@dataclass
class Player:
    name: str
    chips : int = 1000
    is_human : bool = True
    hole_cards: list[Card] = field(default_factory=list)
    current_bet: int = 0
    folded: bool = False
    # TODO: Task 1 - add chips, is_human, hole_cards, current_bet, and folded

    def reset_for_hand(self) -> None:
        self.hole_cards = []
        self.current_bet = 0
        self.folded = False
        # TODO: Task 2 - reset the player's state for a new hand

    def receive(self, cards: list[Card]) -> None:
        for i in cards:
            self.hole_cards.append(i)
        # TODO: Task 3 - add the received cards to the player's hole cards
        pass

    def bet(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Bet amount cannot be negative")
        if self.chips >= amount:
            self.chips = self.chips - amount
            self.current_bet = self.current_bet + amount
            return amount
        else:
            raise ValueError("Not enough chips to place this bet")
        # TODO: Task 4 - check if the player has enough chips to bet the specified amount, 
        # and if so, deduct the amount from the player's chips and add it to the current bet
        
        

    @property
    def active(self) -> bool:
        #return not self.folded
        return self.chips > 0
        # TODO: Task 5 - return True if the player is still active in the hand

