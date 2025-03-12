import random
import hashlib
import secrets

def zkp_generate_permutation_pair(original_deck, seed1=None, seed2=None):
    """
    Generates a pair of permutations for the original deck.
    
    Steps:
    1. If seeds are not provided, generate them randomly.
    2. Shuffle the deck using seed1 to obtain perm1 and compute commitment1.
    3. Shuffle perm1 using seed2 to obtain perm2 and compute commitment2.
    
    :param original_deck: The original deck as a list (e.g., [1, 2, ..., 52])
    :param seed1: (Optional) Seed for the first shuffle.
    :param seed2: (Optional) Seed for the second shuffle.
    :return: A dictionary containing perm1, commitment1, perm2, commitment2, seed1, and seed2.
    """
    if seed1 is None:
        seed1 = secrets.randbits(32)
    if seed2 is None:
        seed2 = secrets.randbits(32)
    
    perm1 = original_deck.copy()
    random.seed(seed1)
    random.shuffle(perm1)
    commitment1 = hashlib.sha256((str(perm1) + str(seed1)).encode()).hexdigest()
    
    perm2 = perm1.copy()
    random.seed(seed2)
    random.shuffle(perm2)
    commitment2 = hashlib.sha256((str(perm2) + str(seed2)).encode()).hexdigest()
    
    return {
        "perm1": perm1,
        "commitment1": commitment1,
        "perm2": perm2,
        "commitment2": commitment2,
        "seed1": seed1,
        "seed2": seed2
    }

def zkp_simulate_challenge(pair_data):
    """
    Simulates Bob's challenge selection for a pair of permutations.
    
    :param pair_data: The dictionary returned by zkp_generate_permutation_pair.
    :return: A challenge_bit (0 or 1).
    """
    return secrets.randbelow(2)

def zkp_reveal_mapping(pair_data, challenge_bit):
    """
    Reveals the mapping according to the challenge selection.
    If challenge_bit == 0, reveals perm1 and seed1.
    If challenge_bit == 1, reveals perm2 and seed2.
    
    :param pair_data: The dictionary from the previous function.
    :param challenge_bit: 0 or 1.
    :return: A dictionary with keys "revealed_mapping" and "seed".
    """
    if challenge_bit == 0:
        return {"revealed_mapping": pair_data["perm1"], "seed": pair_data["seed1"]}
    else:
        return {"revealed_mapping": pair_data["perm2"], "seed": pair_data["seed2"]}

def zkp_verify_mapping(original_source, pair_data, challenge_bit, revealed):
    """
    Verifies that the revealed mapping matches the commitment.
    For challenge_bit == 0: re-shuffle original_source with the provided seed, compute the commitment, and compare with commitment1.
    For challenge_bit == 1: re-shuffle perm1 (from pair_data) with the provided seed, compute the commitment, and compare with commitment2.
    
    :param original_source: If challenge_bit == 0, the original deck; if 1, perm1.
    :param pair_data: The dictionary from zkp_generate_permutation_pair.
    :param challenge_bit: 0 or 1.
    :param revealed: A dictionary with keys "revealed_mapping" and "seed".
    :return: True if verification passes, otherwise False.
    """
    if challenge_bit == 0:
        expected_perm1 = original_source.copy()
        random.seed(revealed["seed"])
        random.shuffle(expected_perm1)
        expected_commitment = hashlib.sha256((str(expected_perm1) + str(revealed["seed"])).encode()).hexdigest()
        return (revealed["revealed_mapping"] == expected_perm1) and (expected_commitment == pair_data["commitment1"])
    else:
        expected_perm2 = pair_data["perm1"].copy()
        random.seed(revealed["seed"])
        random.shuffle(expected_perm2)
        expected_commitment = hashlib.sha256((str(expected_perm2) + str(revealed["seed"])).encode()).hexdigest()
        return (revealed["revealed_mapping"] == expected_perm2) and (expected_commitment == pair_data["commitment2"])

def run_party_round(original_deck):
    """
    Executes a single round of shuffling for one party.
    1. Runs the ZKP process on the deck.
    2. Simulates a challenge selection (0 or 1).
    3. Reveals the mapping according to the challenge.
    4. Verifies the revealed mapping.
    
    :param original_deck: The deck on which the shuffle is performed.
    :return: (new_deck, True) if the round passes, or (None, False) in case of failure.
    """
    pair_data = zkp_generate_permutation_pair(original_deck)
    challenge_bit = zkp_simulate_challenge(pair_data)
    revealed = zkp_reveal_mapping(pair_data, challenge_bit)
    source = original_deck if challenge_bit == 0 else pair_data["perm1"]
    valid = zkp_verify_mapping(source, pair_data, challenge_bit, revealed)
    if not valid:
        return None, False
    new_deck = pair_data["perm1"] if challenge_bit == 0 else pair_data["perm2"]
    return new_deck, True

def run_party_process(original_deck, rounds=100):
    """
    Runs a shuffling process for one party (either Alice or Bob) over a number of rounds.
    
    :param original_deck: The initial deck.
    :param rounds: The number of rounds to perform, default is 100.
    :return: (final_deck, True) if all rounds pass, or (None, False) in case of failure.
    """
    deck = original_deck.copy()
    for i in range(rounds):
        deck, valid = run_party_round(deck)
        if not valid:
            print(f"Party round {i+1} failed!")
            return None, False
    return deck, True
