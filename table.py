"""Shared table state for a Hold'em hand."""
from __future__ import annotations
from cards import Card
from player import Player
 
class Table:
    def __init__(self, table_cards: list = None, players: list[Player] = None, pot: int = 0):
        self.table_cards = []
        self.players = players or []
        self.pot = 0
 
    def reset(self) -> None:
        self.table_cards = []
        self.pot = 0
 
    def add_to_pot(self, amount: int):
        self.pot += amount
