"""Console input/output helpers."""

from __future__ import annotations

from cards import Card
from player import Player


class ConsoleUI: 
    def show_table(self, community_cards: list[Card], pot: int) -> None:
        if community_cards:
            print(f"Board: {self.format_cards(community_cards)}")
        else:
            print("Board: (empty)")
        print(f"Pot: {pot}")

    def show_player(self, player: Player) -> None:
        print(f"{player.name} [{self.format_cards(player.hole_cards)}] - {player.chips} chips")
    
    def ask_action(self, player: Player, call_amount: int) -> str:
        print(f"Options: (c)all {call_amount}, (r)aise, (f)old")
        while True:
            action = input("Your action: ").strip().lower()
            if action in {'c', 'call', 'check'}:
                return 'call'
            elif action in {'r', 'raise'}:
                return 'raise'
            elif action in {'f', 'fold'}:
                return 'fold'
            else:
                print("Invalid action.")

    def ask_raise_amount(self, minimum: int, maximum: int) -> int:
        while True:
            try:
                raise_amount = int(input(f"Enter raise amount (min: {minimum}, max: {maximum}): "))
            except ValueError:
                print("Please enter a valid number")
                continue
            if minimum <= raise_amount <= maximum:
                return raise_amount
            else:
                print("Please enter a valid bet.")

    def show_message(self, message: str) -> None:
        print(message)
    
    def format_cards(self, cards: list[Card]) -> str:
        cards_list = []
        for card in cards:
            cards_list.append(str(card))
        return " ".join(cards_list)