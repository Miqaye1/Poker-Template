"""Run the CLI Texas Hold'em starter game."""
from game import TexasHoldemGame
from player import Player
from table import Table
from evaluator import HandEvaluator
from ui import ConsoleUI

def main() -> None:
    players = [
        Player("You", chips=1000, is_human=True),
        Player("Monte Carlo", chips=1000, is_human=False),
        Player("ML Bot", chips=1000, is_human=False),
    ]
    game = TexasHoldemGame(players, Table(players), HandEvaluator(), ConsoleUI())
    game.play_game()

if __name__ == "__main__":
    main()

