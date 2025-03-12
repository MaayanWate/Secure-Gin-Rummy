
class Player:
    def __init__(self, name, private_keys, public_key):
        """
        Initializes a new player with their name, private keys for decryption, 
        and the public key for encryption.
        """
        self.name = name
        self.hand = []
        self.private_keys = private_keys # Player's private keys for decrypting cards
        self.public_key = public_key # Public key used for encryption

    def sethand(self, toIndex, fromIndex):
        """
        Method to move a card within the player's hand from one index to another.
        This is useful for rearranging cards in the player's hand.
        """
        print(self.hand)
        from encryption import CardEncryption
        encryptor = CardEncryption(self.public_key)  # Encryptor to handle card encryption
        newHand = self.hand
        moved = newHand.pop(fromIndex)
        newHand.insert(toIndex, moved)
        self.hand = newHand
        #self.hand = [encryptor.encrypt_card(card) for card in hand]
        #self.hand = self.hand[::-1]
        #self.hand = hand

    def receive_card(self, encrypted_card):
        """
        Adds an encrypted card to the player's hand.
        """
        self.hand.append(encrypted_card)

    def get_hand_values(self):
        """
        Decrypts all cards in the player's hand and returns their numeric values.
        """
        from encryption import CardEncryption
        decryptor = CardEncryption(self.public_key)
        # Decrypt each card and return the decrypted values
        return [decryptor.decrypt_card(card, self.private_keys) for card in self.hand]

    def reveal_hand(self):
        """
        Reveals the player's hand as card values.
        This decrypts each card and converts it to a string format.
        """
        from encryption import CardEncryption
        decryptor = CardEncryption(self.public_key)
        # Decrypt each card and convert them to strings
        decrypted = [decryptor.decrypt_card(card, self.private_keys) for card in self.hand]
        return [self.card_to_string(val) for val in decrypted]
    
    def play_card(self, card_index, valid_cards, game_state):
        """
        Plays a card from the player's hand, including checking its validity using ZKP.
        The card is checked for validity against the list of valid cards and the current game state.
        """
        if card_index < 0 or card_index >= len(self.hand):
            raise ValueError("Invalid card index")

        # Remove the card from the player's hand
        played_card = self.hand.pop(card_index)

        # Create a Zero Knowledge Proof (ZKP) for the played card to verify its validity
        proof = zkp_valid_move(played_card, valid_cards, game_state)
        if not proof or not verify_valid_move(proof):
            raise ValueError("Invalid move attempted!")

        return played_card  # Return the played card

    def decrypt_card_string(self, encrypted_card):
        """
        Decrypts an encrypted card and converts it into a readable string format.
        """
        from encryption import CardEncryption
        decryptor = CardEncryption(self.public_key)
        # Decrypt the card value and convert it to a string representation
        numeric_value = decryptor.decrypt_card(encrypted_card, self.private_keys)
        return self.card_to_string(numeric_value)

    def card_to_string(self, card_value):
        """
        Converts a numeric card value into a readable string with rank and suit.
        """
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        suit_index = (card_value - 1) // 13
        rank_num = (card_value - 1) % 13 + 1

        if rank_num == 1:
            rank_str = "A"
        elif rank_num == 11:
            rank_str = "J"
        elif rank_num == 12:
            rank_str = "Q"
        elif rank_num == 13:
            rank_str = "K"
        else:
            rank_str = str(rank_num)

        suit_str = suits[suit_index]
        return f"{suit_str} {rank_str}"