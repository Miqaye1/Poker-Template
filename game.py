"""Main Texas Hold'em game loop."""
import ast

from __future__ import annotations

from cards import Deck
from evaluator import HandEvaluator
from player import Player
from table import Table
from ui import ConsoleUI


class TexasHoldemGame:
    def __init__(self, players: list[Player], table: Table, hand_evaluator: HandEvaluator, consoleUI : ConsoleUI, small_blind: int = 5, big_blind: int = 10) -> None:
        if len(players) < 2:
            raise ValueError("There should be at least 2 players to start the game")
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.game_table: Table = table
        self.hand_evaluator: HandEvaluator = hand_evaluator
        self.consoleUI: ConsoleUI = consoleUI
        self.dealer_index = 0

            
        # TODO: Task 1 - check that there are at least 2 players, and if so, 
        # initialize the game state with the players, blinds, table, hand evaluator, and UI
    def play_hand(self) -> None:
        deck = Deck()
        self.game_table.reset()

        for player in self.players:
            player.reset_for_hand()

        for player in self.players:
            player.hole_cards = deck.draw(2)

        self._post_blinds()


        # TODO: Task 2 - implement the main game loop for a single hand of Texas Hold'em, following the 
        # standard sequence of actions (create new Deck, reset table, reset all players, deal two cards to each player, 
        # post blinds, deal (flop, turn, river), run betting rounds, and showdown)
        # NOTE: many of these actions are custom methods
        pass

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
        # TODO: Task 3 - have the first two players post the small and big blinds, 
        # respectively, add those amounts to the pot, 
        # and display the message as "[name] posts [small]; [name] posts [big]"

    def _show_human_cards(self) -> None:
        for player in self.players:
            if player.is_human == True:
                print(f"{player.name}: {player.hole_cards}")
        # TODO: Task 4 - display the hole cards of all human players, e.g. "Alice: AH KH"

    def _deal_community(self, deck: Deck, count: int, street: str) -> None:
        k = 0
        for player in self.players:
            if player.folded == False:
                k = k + 1
        if k <= 1:
            return
        else:
            self.game_table.table_cards.extend(Deck.draw(count))
        # TODO: Task 5 - stop if one player remains, deal the specified number of community 
        # cards from the deck, add them to the table, and display the message as "\n-- [Street] --"
        # HINT: use the extend method of the list to add the new cards to the existing community cards
        pass

def _betting_round(self, street: str) -> None:
    if street == "PreFlop":
        start_player = (self.dealer_index + 3) % len(self.players)
    else:
        start_player = (self.dealer_index + 1) % len(self.players)
        
    betting_not_finished = True
    n = len(self.players)
    i = 0   
    players_who_acted = set()
    
    while betting_not_finished:
        player_index = (start_player + i) % n
        player = self.players[player_index]

        active_players = [p for p in self.players if not p.folded]
        if len(active_players) <= 1:
            betting_not_finished = False
            break
        
        if not player.folded:
            current_bet = max(p.current_bet for p in self.players)
            print(f"{player.name}'s turn")
            print("Choose: fold / call / raise")
            action = input()

            players_who_acted.add(player_index)
            
            if action == "fold":
                player.folded = True
            elif action == "call":
                call_amount = current_bet - player.current_bet
                player.bet(call_amount)
                self.game_table.add_to_pot(call_amount)  # FIX 2a
            elif action == "raise":
                amount = int(input("Raise how much? "))
                total = current_bet - player.current_bet + amount
                player.bet(total)
                self.game_table.add_to_pot(total)  # FIX 2b

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
                break

        i += 1  # FIX 1: was outside the while loop
        # TODO: Task 6 - implement the betting round for the specified street, where each 
        # active player can choose to fold, call, or raise -> ensure that each action works
        # NOTE: this is a big task

    def _bot_action(self, player: Player, call_amount: int) -> str:
        # TODO: Task 7 - implement a simple bot strategy based on the 
        # call amount relative to the player's chips
        
        pass

    def _showdown(self) -> None:
        # TODO: Task 8 - if only one player remains, they win the pot; 
        # otherwise, evaluate the handsof all active players
        # NOTE: this is a big task
        pass 

    def _only_one_player_left(self) -> bool:
        # TODO: Task 9 - return True if only one player is still active and False otherwise
        pass
        #Suren