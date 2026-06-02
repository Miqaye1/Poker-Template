"""Main Texas Hold'em game loop."""
from __future__ import annotations

from cards import Deck
from evaluator import HandEvaluator
from player import Player
from table import Table
from ui import ConsoleUI


class TexasHoldemGame:
    def __init__(self, players, table, hand_evaluator, consoleUI, small_blind=5, big_blind=10):
        if len(players) < 2:
            raise ValueError("There should be at least 2 players to start the game")
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.game_table = table
        self.hand_evaluator = hand_evaluator
        self.consoleUI = consoleUI
        self.dealer_index = 0

    def play_game(self) -> None:
        while True:
            self.players = [p for p in self.players if p.chips > 0]
            if len(self.players) == 1:
                print(f"🏆 {self.players[0].name} wins the game with {self.players[0].chips} chips!")
                break
            print("Chips:")
            for p in self.players:
                print(f"  {p.name}: {p.chips}")
            self.play_hand()
            self.dealer_index = (self.dealer_index + 1) % len(self.players)

    def _monte_carlo(self, player: Player, simulations: int = 200) -> float:
        wins = 0
        known_cards = player.hole_cards + self.game_table.table_cards

        for _ in range(simulations):
            deck = Deck()
            for card in known_cards:
                deck._cards.remove(card)

            community = list(self.game_table.table_cards)
            remaining = 5 - len(community)
            if remaining > 0:                               # fix: skip draw(0) on the River
                community += deck.draw(remaining)

            player_rank = self.hand_evaluator.best_rank(player.hole_cards + community)
            best_rank = player_rank

            for opp in self.players:
                if opp is not player and not opp.folded:
                    opp_rank = self.hand_evaluator.best_rank(deck.draw(2) + community)
                    if opp_rank > best_rank:
                        best_rank = opp_rank

            if player_rank == best_rank:
                wins += 1

        return wins / simulations

    def play_hand(self) -> None:
        deck = Deck()
        self.game_table.reset()
        for player in self.players:
            player.reset_for_hand()
        for player in self.players:
            player.hole_cards = deck.draw(2)
        self._post_blinds()
        self._show_human_cards()
        self._betting_round("PreFlop")
        if not self._only_one_player_left():
            self._deal_community(deck, 3, "Flop")
            self._betting_round("Flop")
        if not self._only_one_player_left():
            self._deal_community(deck, 1, "Turn")
            self._betting_round("Turn")
        if not self._only_one_player_left():
            self._deal_community(deck, 1, "River")
            self._betting_round("River")
        self._showdown()

    def _post_blinds(self) -> None:
        small = (self.dealer_index + 1) % len(self.players)
        big = (self.dealer_index + 2) % len(self.players)
        self.players[small].bet(self.small_blind)
        self.players[big].bet(self.big_blind)
        self.game_table.add_to_pot(self.small_blind)
        self.game_table.add_to_pot(self.big_blind)
        print(f"{self.players[small].name} posts {self.small_blind}; {self.players[big].name} posts {self.big_blind}")

    def _show_human_cards(self) -> None:
        for player in self.players:
            if player.is_human:
                print(f"{player.name}: {self.consoleUI.format_cards(player.hole_cards)}")

    def _deal_community(self, deck, count, street) -> None:
        if self._only_one_player_left():
            return
        self.game_table.table_cards.extend(deck.draw(count))
        print(f"\n-- {street} --")
        print(f"Board: {self.consoleUI.format_cards(self.game_table.table_cards)}")  # fix: show the board

    def _betting_round(self, street: str) -> None:
        if street == "PreFlop":
            start_player = (self.dealer_index + 3) % len(self.players)
        else:
            start_player = (self.dealer_index + 1) % len(self.players)
        betting_not_finished = True
        n = len(self.players)
        i = 0
        players_who_acted: set[int] = set()
        while betting_not_finished:
            player_index = (start_player + i) % n
            player = self.players[player_index]
            active_players = [p for p in self.players if not p.folded]
            if len(active_players) <= 1:
                betting_not_finished = False
                break
            if not player.folded:
                current_bet = max(p.current_bet for p in self.players)
                call_amount = current_bet - player.current_bet
                if player.is_human:
                    self.consoleUI.show_table(self.game_table.table_cards, self.game_table.pot)
                    action = self.consoleUI.ask_action(player, call_amount)
                else:
                    action = self._bot_action(player, call_amount)
                    # fix: print what the bot actually did
                    if action == "fold":
                        print(f"{player.name} folds")
                    elif action == "call":
                        print(f"{player.name} calls {call_amount}")
                    elif action == "raise":
                        print(f"{player.name} raises {self.big_blind}")
                players_who_acted.add(player_index)
                if action == "fold":
                    player.folded = True
                elif action == "call":
                    final_bet = player.bet(call_amount)
                    self.game_table.add_to_pot(final_bet)
                elif action == "raise":
                    if player.is_human:
                        raise_amount = self.consoleUI.ask_raise_amount(minimum=self.big_blind, maximum=player.chips)
                    else:
                        raise_amount = self.big_blind
                    total = call_amount + raise_amount
                    final_bet = player.bet(total)
                    self.game_table.add_to_pot(final_bet)
                active_players = [p for p in self.players if not p.folded]
                if len(active_players) <= 1:
                    betting_not_finished = False
                    break
                all_active_have_acted = all(self.players.index(p) in players_who_acted for p in active_players)
                first_active_bet = active_players[0].current_bet
                all_bets_equal = all(p.current_bet == first_active_bet for p in active_players)
                if all_active_have_acted and all_bets_equal:
                    betting_not_finished = False
            i += 1

    def _bot_action(self, player: Player, call_amount: int) -> str:
        win_prob = self._monte_carlo(player)

        if call_amount == 0:
            return "raise" if win_prob > 0.6 else "call"

        pot_odds = call_amount / (self.game_table.pot + call_amount)

        if win_prob > 0.65:
            return "raise"
        elif win_prob >= pot_odds:
            return "call"
        else:
            return "fold"

    def _showdown(self) -> None:
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.game_table.pot
            print(f"\n{winner.name} wins {self.game_table.pot} chips (everyone else folded)!")
            return
        print("\n-- Showdown --")
        best_rank = None
        winner = None
        for player in active_players:
            all_cards = player.hole_cards + self.game_table.table_cards
            rank = self.hand_evaluator.best_rank(all_cards)
            hand_name = rank.category_name()
            print(f"{player.name}: {self.consoleUI.format_cards(player.hole_cards)} → {hand_name}")
            if best_rank is None or rank > best_rank:
                best_rank = rank
                winner = player
        winner.chips += self.game_table.pot
        print(f"\n{winner.name} wins {self.game_table.pot} chips with {best_rank.category_name()}!")

    def _only_one_player_left(self) -> bool:
        active_players = [p for p in self.players if not p.folded]
        return len(active_players) <= 1