"""Shared table state for a Hold'em hand."""

from __future__ import annotations

from dataclasses import dataclass, field

from cards import Card
from player import Player


# TODO: Task 1 - implement the Table class 
class Table:
    def __init__(self, table_cards: list, players: list[Player], pot: int):
        self.table_cards = []
        self.players = players
        self.pot = 0
    def reset(self) -> None:
        self.table_cards = []
        self.pot = 0
    def add_to_pot(self, amount: int):
        self.pot += amount
    # TODO: Task 2 - create and implement the method reset(self) -> None 
    # TODO: Task 3 - create and implement the method add_to_pot(self, amount: int) -> None
