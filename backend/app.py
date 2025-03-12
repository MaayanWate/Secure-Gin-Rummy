from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room
import encryption
from game import Game

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize a new game (including scores)
game = Game()

@app.route("/start_game", methods=["GET"])
def start_game():
    """
    Endpoint to start a new game. It initializes the game by resetting 
    the game state.
    """
    global game
    game = Game()
    return jsonify({"message": "Game started!"})

@socketio.on("new_hand")
def handle_new_hand(data):
    """
    Event handler for dealing a new hand to a player. 
    """
    player = data.get("player")
    toIndex = data.get("toIndex")
    fromIndex = data.get("fromIndex")
    game.players[player].sethand(toIndex, fromIndex)  # Update player's hand with new cards

@socketio.on("join_game")
def handle_join(data):
    """
    Event handler for when a player joins the game. The player's hand is 
    encrypted.
    """
    player = data.get("player")
    if not player:
        print("Error: No player id provided in join_game event!")
        return
    join_room(player)

    player_encrypted_hand = game.players[player].hand
    opponent = "player1" if player == "player2" else "player2"
    opponent_count = len(game.players[opponent].hand)

    # Initial state to send to the player, informing them of the game status
    initial_state = {
        "message": f"Joined as {player}",
        "deck_size": len(game.deck.encrypted_deck),
        "turn": game.turn,
        "pending": game.pending,
        "hand": game.players[player].reveal_hand(),
        "opponent_count": opponent_count,
        "discard_string": game.discard_string,
        "scores": game.scores
    }
    emit("update_game", initial_state, room=player)

@socketio.on("draw_card")
def handle_draw_card(data):
    """
    Event handler for when a player draws a card. It checks whether the action is 
    valid. After a valid draw, the game state is updated and sent to both players.
    """
    player = data["player"]
    source = data.get("source", "stock")
    response = game.draw_card(player, source)

    if "error" in response:
        player_hand = game.players[player].reveal_hand()
        opponent = "player1" if player == "player2" else "player2"
        opponent_count = len(game.players[opponent].hand)
        error_state = {
            "message": response["error"],
            "deck_size": len(game.deck.encrypted_deck),
            "turn": game.turn,
            "pending": game.pending,
            "hand": player_hand,
            "opponent_count": opponent_count,
            "discard_string": game.discard_string,
            "scores": game.scores
        }
        emit("update_game", error_state, room=player)
        return

    # If the card is valid, update the game state and send the updated info to both players
    player_hand = game.players[player].reveal_hand()
    opponent = "player1" if player == "player2" else "player2"
    opponent_count = len(game.players[opponent].hand)

    current_response = {
        "message": response.get("message", ""),
        "deck_size": response.get("deck_size"),
        "turn": game.turn,
        "pending": game.pending,
        "hand": player_hand,
        "opponent_count": opponent_count,
        "discard_string": game.discard_string,
        "scores": game.scores
    }
    
    opponent_response = {
        "deck_size": response.get("deck_size"),
        "turn": game.turn,
        "pending": game.pending,
        "opponent_count": len(game.players[player].hand),
        "discard_string": game.discard_string,
        "scores": game.scores
    }

    emit("update_game", current_response, room=player)
    emit("update_game", opponent_response, room=opponent)

@socketio.on("discard_card")
def handle_discard_card(data):
    """
    Event handler for when a player discards a card. If a player wins after discarding, 
    the round is concluded, and the result is broadcast to all players.
    """
    player = data["player"]
    card_index = data.get("cardIndex")
    response = game.discard_card(player, card_index)
    
    if "error" in response:
        player_hand = game.players[player].reveal_hand()
        opponent = "player1" if player == "player2" else "player2"
        opponent_count = len(game.players[opponent].hand)
        error_state = {
            "message": response["error"],
            "deck_size": len(game.deck.encrypted_deck),
            "turn": game.turn,
            "pending": game.pending,
            "hand": player_hand,
            "opponent_count": opponent_count,
            "discard_string": game.discard_string,
            "scores": game.scores
        }
        emit("update_game", error_state, room=player)
        return

    winner_info = game.check_for_winner(player)
    if winner_info:
        final_result = game.check_game_over()
        if final_result:
            socketio.emit("game_over", final_result)
        else:
            socketio.emit("round_over", winner_info)
        return

    player_hand = game.players[player].reveal_hand()
    opponent = "player1" if player == "player2" else "player2"
    opponent_count = len(game.players[opponent].hand)

    current_response = {
        "message": response.get("message", ""),
        "deck_size": response.get("deck_size"),
        "turn": game.turn,
        "pending": game.pending,
        "hand": player_hand,
        "opponent_count": opponent_count,
        "discard_string": game.discard_string,
        "scores": game.scores
    }
    opponent_response = {
        "deck_size": response.get("deck_size"),
        "turn": game.turn,
        "pending": game.pending,
        "opponent_count": len(game.players[player].hand),
        "discard_string": game.discard_string,
        "scores": game.scores
    }

    emit("update_game", current_response, room=player)
    emit("update_game", opponent_response, room=opponent)

@socketio.on("knock")
def handle_knock(data):
    """
    Event handler for when a player knocks, signaling the end of the round.
    After the knock, the game checks for the winner and sends the result.
    """
    player = data["player"]
    response = game.knock(player)
    if "error" in response:
        emit("knock_error", response, room=player)
    else:
        final_result = game.check_game_over()
        if final_result:
            socketio.emit("game_over", final_result)
        else:
            socketio.emit("round_over", response)

@socketio.on("new_round")
def handle_new_round():
    """
    This function handles the start of a new round. It resets the round state
    (without resetting the scores) and sends the updated game state to each player.
    """
    game.reset_round(reset_scores=False)
    for p in game.players:
        p_hand = game.players[p].reveal_hand()
        opp = "player1" if p == "player2" else "player2"
        opp_count = len(game.players[opp].hand)
        new_state = {
            "message": "New round started",
            "deck_size": len(game.deck.encrypted_deck),
            "turn": game.turn,
            "pending": game.pending,
            "hand": p_hand,
            "opponent_count": opp_count,
            "discard_string": game.discard_string,
            "scores": game.scores
        }
        emit("update_game", new_state, room=p)

@socketio.on("new_game")
def handle_new_game():
    """
    This function starts a completely new game. It resets all game elements, including the score,
    shuffles and deals new cards, and broadcasts the new game state to all players.
    """
    global game
    game = Game()
    print("[new_game] Current turn:", game.turn)
    for p in game.players:
        p_hand = game.players[p].reveal_hand()
        opp = "player1" if p == "player2" else "player2"
        opp_count = len(game.players[opp].hand)
        game_state = {
            "message": "New game started",
            "deck_size": len(game.deck.encrypted_deck),
            "turn": game.turn,
            "pending": game.pending,
            "hand": p_hand,
            "opponent_count": opp_count,
            "discard_string": game.discard_string,
            "scores": game.scores
        }
        socketio.sleep(0.1)
        emit("update_game", game_state, room=p)
    
    broadcast_state = {
        "message": "A new game has started!",
        "scores": game.scores,
        "turn": game.turn,
        "discard_string": game.discard_string,
        "deck_size": len(game.deck.encrypted_deck)
    }
    socketio.sleep(0.1)
    emit("update_game", broadcast_state, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
