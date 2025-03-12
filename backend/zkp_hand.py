import hashlib
import secrets

def generate_salt():
    """Generates a secure random salt."""
    return secrets.token_hex(16)

def create_hand_commitments(hand):
    """
    Computes a commitment for each card in the hand by concatenating the card value with a salt
    and then applying the SHA-256 hash function.
    
    :param hand: A list of cards (e.g., [card1, card2, ...])
    :return: A dictionary mapping each card to a tuple (commitment, salt)
    """
    commitments = {}
    for card in hand:
        salt = generate_salt()
        commitment = hashlib.sha256((str(card) + salt).encode()).hexdigest()
        commitments[card] = (commitment, salt)
    return commitments

def generate_discard_proof(card, commitments):
    """
    Generates a discard proof for the selected card by revealing its corresponding salt.
    
    :param card: The card being discarded
    :param commitments: A dictionary containing the commitments for all cards in the hand
    :return: A proof dictionary with keys "card" and "salt"
    """
    if card in commitments:
        commitment, salt = commitments[card]
        # The proof simply reveals the card and its salt.
        proof = {"card": card, "salt": salt}
        return proof
    else:
        raise Exception("Card not found in hand commitments!")

def verify_discard_proof(proof, commitments):
    """
    Verifies the discard proof by computing the SHA-256 hash of (card + salt) and comparing it
    to the stored commitment.
    
    :param proof: A dictionary with keys "card" and "salt" provided by the discarding player
    :param commitments: The dictionary of initial commitments
    :return: True if the proof matches the stored commitment, otherwise False.
    """
    card = proof["card"]
    salt = proof["salt"]
    computed = hashlib.sha256((str(card) + salt).encode()).hexdigest()
    stored = commitments.get(card, (None,))[0]
    return computed == stored
