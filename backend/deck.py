import random
from encryption import CardEncryption

class Deck:
    def __init__(self, public_key):
        """
        Initializes the deck with shuffled cards and encrypts them.
        
        Args:
            public_key: The public key used for encrypting the cards.
            
        Steps:
            1. Creates a list of cards numbered 1 to 52.
            2. Performs an initial shuffle using random.shuffle.
            3. Initializes the CardEncryption instance with the provided public key.
            4. Encrypts each card in the shuffled deck.
            
        Note: The final secure shuffle (using the ZKP protocol) will be performed in the game reset_round method.
        """
        self.cards = list(range(1, 53))
        random.shuffle(self.cards)  # Initial simple shuffle
        
        # Initialize the encryption system with the public key.
        self.encryption = CardEncryption(public_key)
        
        # Encrypt each card in the deck.
        self.encrypted_deck = [self.encryption.encrypt_card(card) for card in self.cards]

    def draw_card(self):
        """
        Draws (removes) the top card from the encrypted deck.
        
        Returns:
            The encrypted card if available, or None if the deck is empty.
        """
        if self.encrypted_deck:
            return self.encrypted_deck.pop(0)
        return None
