import csv
from game import TexasHoldemGame
from player import Player
from table import Table
from evaluator import HandEvaluator
from ui import ConsoleUI

STREETS = {"PreFlop": 0, "Flop": 1, "Turn": 2, "River": 3}

class RecordingGame(TexasHoldemGame):
    def __init__(self, players, table, evaluator, ui, writer):
        super().__init__(players, table, evaluator, ui, silent=True)
        self.writer = writer
        self.current_street = "PreFlop"
        self.decisions = []

    def _betting_round(self, street: str) -> None:
        self.current_street = street
        super()._betting_round(street)

    def _bot_action(self, player, call_amount):
        win_prob = self._monte_carlo(player, simulations=50)
        pot = self.game_table.pot
        pot_odds = call_amount / (pot + call_amount) if (pot + call_amount) > 0 else 0

        if win_prob > 0.85:
            raise_amount = min(pot, player.chips)
        elif win_prob > 0.75:
            raise_amount = min(self.big_blind * 3, player.chips)
        else:
            raise_amount = min(self.big_blind * 2, player.chips)

        if call_amount == 0:
            action = "raise" if win_prob > 0.6 else "call"
        elif win_prob > 0.65:
            action = "raise"
        elif win_prob >= pot_odds:
            action = "call"
        else:
            action = "fold"

        self.decisions.append({
            "player": player.name,
            "win_probability": win_prob,
            "pot_odds": pot_odds,
            "street": STREETS[self.current_street],
            "stack_to_pot": player.chips / pot if pot > 0 else 999,
            "opponent_bet_ratio": call_amount / pot if pot > 0 else 0,
            "players_left": len([p for p in self.players if not p.folded]),
            "action": action,
            "won_hand": None
        })

        return action, raise_amount if action == "raise" else 0

    def _showdown(self) -> None:
        active_players = [p for p in self.players if not p.folded]

        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.game_table.pot
        else:
            winner = max(
                active_players,
                key=lambda p: self.hand_evaluator.best_rank(p.hole_cards + self.game_table.table_cards)
            )
            winner.chips += self.game_table.pot

        for decision in self.decisions:
            decision["won_hand"] = (decision["player"] == winner.name)
            d = {k: v for k, v in decision.items() if k != "player"}
            self.writer.writerow(d)

        self.decisions = []


def run_simulations(num_games: int = 5000):
    with open("poker_data.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "win_probability", "pot_odds", "street",
            "stack_to_pot", "opponent_bet_ratio",
            "players_left", "action", "won_hand"
        ])
        writer.writeheader()

        for i in range(num_games):
            players = [
                Player("Bot1", chips=1000, is_human=False),
                Player("Bot2", chips=1000, is_human=False),
                Player("Bot3", chips=1000, is_human=False),
            ]
            table = Table(players)
            evaluator = HandEvaluator()
            ui = ConsoleUI()

            game = RecordingGame(players, table, evaluator, ui, writer)
            game.play_hand()

            if i % 500 == 0:
                print(f"Simulated {i}/{num_games} hands...")

    print("Done! Data saved to poker_data.csv")


if __name__ == "__main__":
    run_simulations(200)