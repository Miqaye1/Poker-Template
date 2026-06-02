"""Main Texas Hold'em game loop."""
from __future__ import annotations  # BUG FIX 1: must be the very first line, was after imports

# BUG FIX 2: removed unused `import ast`
from cards import Deck
from evaluator import HandEvaluator
from player import Player
from table import Table
from ui import ConsoleUI


class TexasHoldemGame:
    def __init__(
        self,
        players: list[Player],
        table: Table,
        hand_evaluator: HandEvaluator,
        consoleUI: ConsoleUI,
        small_blind: int = 5,
        big_blind: int = 10,
    ) -> None:
        if len(players) < 2:
            raise ValueError("There should be at least 2 players to start the game")
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.game_table: Table = table
        self.hand_evaluator: HandEvaluator = hand_evaluator
        self.consoleUI: ConsoleUI = consoleUI
        self.dealer_index = 0

    def play_hand(self) -> None:
        deck = Deck()
        self.game_table.reset()

        for player in self.players:
            player.reset_for_hand()

        for player in self.players:
            player.hole_cards = deck.draw(2)

        self._post_blinds()
        self._show_human_cards()

        # BUG FIX 5: complete the full hand sequence instead of just `pass`
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
        # yours to complete

    def _post_blinds(self) -> None:
        small = (self.dealer_index + 1) % len(self.players)
        big = (self.dealer_index + 2) % len(self.players)

        self.players[small].bet(self.small_blind)
        self.players[big].bet(self.big_blind)

        self.game_table.add_to_pot(self.small_blind)
        self.game_table.add_to_pot(self.big_blind)

        print(
            f"{self.players[small].name} posts {self.small_blind}; "
            f"{self.players[big].name} posts {self.big_blind}"
        )

    def _show_human_cards(self) -> None:
        for player in self.players:
            if player.is_human:
                print(f"{player.name}: {player.hole_cards}")

    def _deal_community(self, deck: Deck, count: int, street: str) -> None:
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
                # BUG FIX 7: was using raw input() and print() for all players, including bots.
                # Humans should go through the UI; bots through _bot_action.
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
                    actual = player.bet(call_amount)
                    self.game_table.add_to_pot(actual)
                elif action == "raise":
                    if player.is_human:
                        raise_amount = self.consoleUI.ask_raise_amount(
                            minimum=self.big_blind, maximum=player.chips
                        )
                    else:
                        raise_amount = self.big_blind  # bots raise the minimum
                    total = call_amount + raise_amount
                    actual = player.bet(total)
                    self.game_table.add_to_pot(actual)

                active_players = [p for p in self.players if not p.folded]
                if len(active_players) <= 1:
                    betting_not_finished = False
                    break

                all_active_have_acted = all(
                    self.players.index(p) in players_who_acted for p in active_players
                )
                first_active_bet = active_players[0].current_bet
                all_bets_equal = all(p.current_bet == first_active_bet for p in active_players)

                if all_active_have_acted and all_bets_equal:
                    betting_not_finished = False

            i += 1

    def _bot_action(self, player: Player, call_amount: int) -> str:
        # BUG FIX 8: was just `pass`, which returns None and breaks the betting logic
        if call_amount == 0:
            return "raise"
        if call_amount > player.chips * 0.2:
            return "fold"
        return "call"

    def _showdown(self) -> None:
        active_players = [p for p in self.players if not p.folded]

        # It's still correct to check here — everyone could have folded by now
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
            print(
                f"{player.name}: {self.consoleUI.format_cards(player.hole_cards)}"
                f" → {hand_name}"
            )
            if best_rank is None or rank > best_rank:
                best_rank = rank
                winner = player

        winner.chips += self.game_table.pot
        print(f"\n{winner.name} wins {self.game_table.pot} chips with {best_rank.category_name()}!")
        # TODO: Task 8 - if only one player remains, they win the pot; 
        # otherwise, evaluate the handsof all active players
        # NOTE: this is a big task

    def _only_one_player_left(self) -> bool:
        # TODO: Task 9 - return True if only one player is still active and False otherwise
        active_players = [p for p in self.players if not p.folded]
        return len(active_players) <= 1