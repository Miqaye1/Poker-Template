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
            # Remove players who have run out of chips
            self.players = [p for p in self.players if p.chips > 0]
            if len(self.players) == 1:
                print(f"🏆 {self.players[0].name} wins the game with {self.players[0].chips} chips!")
                break
            print("Chips:")
            for p in self.players:
                print(f"  {p.name}: {p.chips}")
            self.play_hand()
            self.dealer_index = (self.dealer_index + 1) % len(self.players)
 
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
 
    def _bot_action(self, player, call_amount) -> str:
        if call_amount == 0:
            return "raise"
        if call_amount > player.chips * 0.2:
            return "fold"
        return "call"
 
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