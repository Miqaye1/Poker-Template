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

    def reset_for_hand(self) -> None:
        self.hole_cards = []
        self.current_bet = 0
        self.folded = False

    def receive(self, cards: list[Card]) -> None:
        for i in cards:
            self.hole_cards.append(i)

    def bet(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Bet amount cannot be negative")
        amount = min(amount, self.chips)
        self.chips -= amount
        self.current_bet += amount
        return amount
        
        
    @property
    def active(self) -> bool:
        return not self.folded

