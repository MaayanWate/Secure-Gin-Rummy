from deck import Deck
from player import Player
from encryption import CardEncryption
from itertools import combinations
import random
from zkp import run_party_process  # Import secure shuffle process
from zkp_hand import create_hand_commitments, generate_discard_proof, verify_discard_proof

def get_rank(card_value):
    """
    Retrieves the rank of the card based on its value.
    """
    return (card_value - 1) % 13 + 1

def get_suit(card_value):
    """
    Retrieves the suit of the card based on its value.
    """
    return (card_value - 1) // 13

def card_points(rank):
    """
    Determines the points of a card based on its rank.
    """
    if rank == 1:
        return 1
    elif rank >= 11:
        return 10
    else:
        return rank

def remove_cards(full_list, subset):
    """
    Removes a list of cards (subset) from the full list and returns the remaining cards.
    """
    remaining = list(full_list)
    for card in subset:
        remaining.remove(card)
    return remaining

def _best_deadwood_recursive(card_list):
    """
    Recursively calculates the minimum deadwood value (the total value of ungrouped cards).
    It tries to group cards into valid sets (3 or 4 of the same rank) or runs (sequences of 3+ cards in the same suit).
    """
    if not card_list:
        return 0
    first = card_list[0]
    rest = card_list[1:]
    best_score = card_points(first[0]) + _best_deadwood_recursive(rest)

    # Check for sets of the same rank (3 or 4 cards of the same rank)
    same_rank = [c for c in card_list if c[0] == first[0]]
    for group_size in [3, 4]:
        if len(same_rank) >= group_size:
            from itertools import combinations
            for combo in combinations(same_rank, group_size):
                remaining = remove_cards(card_list, list(combo))
                score = _best_deadwood_recursive(remaining)
                if score < best_score:
                    best_score = score

    # Check for runs (sequences of cards in the same suit)
    run_suit = first[1]
    same_suit = [c for c in card_list if c[1] == run_suit]
    runs = find_all_runs(same_suit)
    for run_group in runs:
        if first in run_group:
            remaining = remove_cards(card_list, run_group)
            score = _best_deadwood_recursive(remaining)
            if score < best_score:
                best_score = score

    return best_score

def find_all_runs(cards_same_suit):
    """
    Finds all possible runs (sequences of 3 or more consecutive cards) within a given set of cards of the same suit.
    """
    if len(cards_same_suit) < 3:
        return []
    sorted_cards = sorted(cards_same_suit, key=lambda x: x[0])
    results = []
    def backtrack(start, current):
        if start >= len(sorted_cards):
            if len(current) >= 3:
                results.append(current[:])
            return
        if not current or sorted_cards[start][0] == current[-1][0] + 1:
            current.append(sorted_cards[start])
            backtrack(start+1, current)
            current.pop()
        backtrack(start+1, current)
    backtrack(0, [])
    return [r for r in results if len(r) >= 3]

def compute_min_deadwood(card_values):
    """
    Computes the minimum deadwood score by evaluating a list of card values.
    """
    card_list = []
    for val in card_values:
        r = get_rank(val)
        s = get_suit(val)
        card_list.append((r, s))
    card_list.sort(key=lambda x: (x[1], x[0]))
    return _best_deadwood_recursive(card_list)

class Game:
    def __init__(self):
        """
        Initializes a new game, sets up the encryption system, creates the deck,
        performs a secure shuffle, deals the initial cards, and verifies the initial shuffle.
        """
        self.public_key, self.private_keys = CardEncryption.generate_keys()
        self.deck = Deck(self.public_key)
        
        # Perform secure shuffle using run_party_process (cryptographic shuffle)
        deck_after_alice, alice_ok = run_party_process(self.deck.cards, rounds=100)
        assert alice_ok, "Alice's secure shuffle failed!"
        deck_final, bob_ok = run_party_process(deck_after_alice, rounds=100)
        assert bob_ok, "Bob's secure shuffle failed!"
        
        # Update deck with the final order and re-encrypt cards
        self.deck.cards = deck_final
        self.deck.encrypted_deck = [self.deck.encryption.encrypt_card(card) for card in self.deck.cards]
        
        # Initialize two players with their private and public keys
        self.players = {
            "player1": Player("Player 1", self.private_keys, self.public_key),
            "player2": Player("Player 2", self.private_keys, self.public_key)
        }
        # Deal 10 cards to each player
        for _ in range(10):
            for plr in self.players.values():
                plr.receive_card(self.deck.draw_card())

        # Draw the first card for discard pile
        first_discard = self.deck.draw_card()
        self.discard = first_discard
        self.discard_string = self.players["player1"].decrypt_card_string(first_discard)

        # Set the turn to player1
        self.turn = "player1"
        self.pending = None
        self.scores = {"player1": 0, "player2": 0}

    def draw_card(self, player_name, source):
        """
        Allows a player to draw a card from the stock or discard pile.
        Verifies if it's the player's turn and whether they have already discarded before drawing.
        """
        if self.turn != player_name:
            return {"error": "Not your turn!"}
        if self.pending is not None:
            return {"error": "You must discard before drawing again!"}
        
        # Set pending immediately to block double clicks
        self.pending = player_name

        if source == "stock":
            card = self.deck.draw_card()
            if not card:
                self.pending = None  # Reset pending if draw fails
                return {"error": "No cards left in stock!"}
        elif source == "discard":
            if not self.discard:
                self.pending = None
                return {"error": "No card in discard pile!"}
            card = self.discard
            self.discard = None
            self.discard_string = None
        else:
            self.pending = None
            return {"error": "Invalid source!"}

        self.players[player_name].receive_card(card)

        return {
            "message": f"{player_name} drew a card from {source}",
            "deck_size": len(self.deck.encrypted_deck),
            "turn": self.turn,
            "pending": self.pending,
            "scores": self.scores
        }

    def discard_card(self, player_name, card_index):
        """
        Allows a player to discard a card from their hand.
        Verifies if the player has drawn a card before attempting to discard.
        Additionally, performs discard validation using ZKP to ensure that the discarded card 
        was indeed part of the player's hand.
        """
        if self.pending != player_name:
            return {"error": "You must draw a card before discarding!"}
        player = self.players[player_name]
        if card_index < 0 or card_index >= len(player.hand):
            return {"error": "Invalid card index"}

        # Generate commitments for the player's hand using ZKP (without exposing all details)
        hand_commitments = create_hand_commitments(player.hand)
        
        # Get the card that is about to be discarded
        discarded_card = player.hand[card_index]
        
        # Generate discard proof for the card using its commitment
        proof = generate_discard_proof(discarded_card, hand_commitments)
        
        # Verify the discard proof
        if not verify_discard_proof(proof, hand_commitments):
            return {"error": "Discard validation failed. The card is not part of your hand."}

        # If validation passes, remove the card from the hand
        player.hand.pop(card_index)
        self.discard = discarded_card
        self.discard_string = player.decrypt_card_string(discarded_card)
        self.pending = None
        self.turn = "player2" if player_name == "player1" else "player1"

        return {
            "message": f"{player_name} discarded a card",
            "deck_size": len(self.deck.encrypted_deck),
            "turn": self.turn,
            "discard_string": self.discard_string,
            "scores": self.scores
        }

    def knock(self, player_name):
        """
        Handles the knock action where a player ends their turn to reveal their deadwood.
        Determines if the player wins or if the opponent's deadwood is lower.
        """
        knocker = self.players[player_name]
        defender_name = "player1" if player_name == "player2" else "player2"
        defender = self.players[defender_name]

        knocker_deadwood = compute_min_deadwood(knocker.get_hand_values())
        defender_deadwood = compute_min_deadwood(defender.get_hand_values())

        if knocker_deadwood > 10:
            return {"error": "Knock is not possible! Your deadwood is too high."}

        if knocker_deadwood == 0:
            # Gin / Big Gin
            if len(knocker.hand) == 11:
                points = 31 + defender_deadwood
                result = {"winner": player_name, "reason": "Big Gin", "points": points}
            else:
                points = 25 + defender_deadwood
                result = {"winner": player_name, "reason": "Gin", "points": points}
            self.scores[player_name] += points
            return result

        # Regular Knock
        if defender_deadwood <= knocker_deadwood:
            points = (knocker_deadwood - defender_deadwood) + 25
            self.scores[defender_name] += points
            result = {"winner": defender_name, "reason": "Undercut", "points": points}
        else:
            points = defender_deadwood - knocker_deadwood
            self.scores[player_name] += points
            result = {"winner": player_name, "reason": "Knock", "points": points}

        return result

    def check_for_winner(self, player_name):
        """
        Checks if a player has won by reaching 0 deadwood and has a valid hand (Gin or Big Gin).
        """
        player = self.players[player_name]
        decrypted_values = player.get_hand_values()
        deadwood_value = sum(decrypted_values)
        if deadwood_value == 0 and len(decrypted_values) == 10:
            return {"winner": player_name, "reason": "Gin!", "points": 25}
        elif deadwood_value == 0 and len(decrypted_values) == 11:
            return {"winner": player_name, "reason": "Big Gin!", "points": 31}
        elif deadwood_value <= 10:
            return {"winner": player_name, "reason": "Knock!", "points": deadwood_value}
        return None

    def check_game_over(self):
        """
        Checks if any player has reached the required score to win the game.
        """
        for player, score in self.scores.items():
            if score >= 100:
                return {"winner": player, "score": score}
        return None

    def reset_round(self, reset_scores=False):
        """
        Resets the round by creating a new deck, performing secure shuffling,
        and redealing the cards.
        """
        if reset_scores:
            self.scores = {"player1": 0, "player2": 0}

        # Create a new deck
        self.deck = Deck(self.public_key)

        # *** Secure shuffle process ***
        # Step 1: "Alice" shuffles 100 times on the initial deck
        deck_after_alice, alice_ok = run_party_process(self.deck.cards, rounds=100)
        assert alice_ok, "Alice's secure shuffle failed!"

        # Step 2: "Bob" shuffles 100 times on the deck received from Alice
        deck_final, bob_ok = run_party_process(deck_after_alice, rounds=100)
        assert bob_ok, "Bob's secure shuffle failed!"

        # Update deck with the final order and re-encrypt cards
        self.deck.cards = deck_final
        self.deck.encrypted_deck = [self.deck.encryption.encrypt_card(card) for card in self.deck.cards]

        # Clear player hands and redeal
        for plr in self.players.values():
            plr.hand = []
        for _ in range(10):
            for plr in self.players.values():
                plr.receive_card(self.deck.draw_card())

        # Draw the first card for the discard pile
        first_discard = self.deck.draw_card()
        self.discard = first_discard
        self.discard_string = self.players["player1"].decrypt_card_string(first_discard)
        self.turn = "player1"
        self.pending = None
