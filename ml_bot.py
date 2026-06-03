import joblib
import pandas as pd

STREETS = {"PreFlop": 0, "Flop": 1, "Turn": 2, "River": 3}

class MLBot:
    def __init__(self, model_path: str = "poker_model.pkl"):
        self.model = joblib.load(model_path)

    def decide(self, player, game, call_amount: int, street: str) -> tuple[str, int]:
        pot = game.game_table.pot
        win_probability = game._monte_carlo(player)
        pot_odds = call_amount / (pot + call_amount) if (pot + call_amount) > 0 else 0
        stack_to_pot = player.chips / pot if pot > 0 else 999
        opponent_bet_ratio = call_amount / pot if pot > 0 else 0
        players_left = len([p for p in game.players if not p.folded])

        features = pd.DataFrame([[
            win_probability,
            pot_odds,
            STREETS[street],
            stack_to_pot,
            opponent_bet_ratio,
            players_left
        ]], columns=["win_probability", "pot_odds", "street", "stack_to_pot", "opponent_bet_ratio", "players_left"])

        action = self.model.predict(features)[0]

        # Calculate raise amount the same way the teacher does
        if action == "raise":
            if win_probability > 0.85:
                raise_amount = min(pot, player.chips)
            elif win_probability > 0.75:
                raise_amount = min(game.big_blind * 3, player.chips)
            else:
                raise_amount = min(game.big_blind * 2, player.chips)
        else:
            raise_amount = 0

        return action, raise_amount