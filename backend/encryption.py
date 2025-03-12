from Crypto.Util.number import getPrime, inverse
import random
import hashlib

class CardEncryption:
    def __init__(self, public_key):
        """
        Initializes the encryption system using a public key.

        The public key consists of the values (p, g, y), where:
        - p is a 256-bit prime number
        - g is a generator
        - y is the public component computed as g^(x1 * x2) mod p
        """
        self.public_key = public_key

    @staticmethod
    def generate_keys():
        """
        Generates the public and private keys for ElGamal encryption.
        
        The public key is (p, g, y) where:
        - p is a prime number
        - g is a generator
        - y = g^(x1 * x2) mod p (public key)

        The private keys are (x1, x2) where:
        - x1 and x2 are random private integers used to generate the public key.
        
        This setup is inspired by threshold cryptography, splitting the private key into two parts.
        """
        p = getPrime(256)  # p is a 256-bit prime
        g = random.randint(2, p - 1)  # g is a random generator in the range [2, p-1]
        x1 = random.randint(1, p - 2)  # x1 is a random private key component
        x2 = random.randint(1, p - 2)  # x2 is another random private key component
        y = pow(g, x1 * x2, p)  # Public key component y = g^(x1 * x2) mod p
        return (p, g, y), (x1, x2)  # Returns public and private keys

    def encrypt_card(self, card_value):
        """
        Encrypts a card value using ElGamal encryption.

        The card is encrypted using the public key (p, g, y) and a random ephemeral key k.
        
        Encryption:
        - c1 = g^k mod p (first component of the ciphertext)
        - c2 = card_value * y^k mod p (second component of the ciphertext)

        This encryption ensures privacy, as the card value is transformed using public information.
        """
        p, g, y = self.public_key  # Extract public key components
        k = random.randint(1, p - 2)  # Random ephemeral key k
        c1 = pow(g, k, p)  # First component of the ciphertext: g^k mod p
        c2 = (card_value * pow(y, k, p)) % p  # Second component: card_value * y^k mod p
        return c1, c2  # Returns the encrypted card as a tuple (c1, c2)

    def decrypt_card(self, encrypted_card, private_keys):
        """
        Decrypts an encrypted card using the private keys (x1, x2).
        
        The decryption uses the private keys to recover the original card value.

        Decryption:
        - Compute s = c1^(x1 * x2) mod p
        - Find the modular inverse of s mod p
        - Recover the card value: card_value = c2 * s^(-1) mod p
        """
        p, _, _ = self.public_key  # Extract the public key's p component
        c1, c2 = encrypted_card  # Extract the encrypted components
        x1, x2 = private_keys  # Extract the private keys
        s = pow(c1, x1 * x2, p)  # Compute s = c1^(x1 * x2) mod p
        s_inv = inverse(s, p)  # Compute the modular inverse of s mod p
        return (c2 * s_inv) % p  # Recover the original card value using the modular inverse

