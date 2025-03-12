import React, { useEffect, useState } from "react";
import Card from "./Card"; // Component for displaying a card in the discard pile
import Player from "./Player";

function Board({ socket }) {
  // State variables for managing game data
  const [deckSize, setDeckSize] = useState(52);
  const [playerTurn, setPlayerTurn] = useState("");
  const [message, setMessage] = useState("");
  const [myHand, setMyHand] = useState([]);
  const [playerId, setPlayerId] = useState("");
  const [pending, setPending] = useState(null);
  const [discardString, setDiscardString] = useState(null);
  const [scores, setScores] = useState({ player1: 0, player2: 0 });
  const [gameOver, setGameOver] = useState(false);
  const [roundFinished, setRoundFinished] = useState(false); // Indicates that the round has ended and "Next Round" has been pressed
  const [isDrawing, setIsDrawing] = useState(false);
  const [, setUpdate] = useState(0);
  const forceUpdate = () => {
    setUpdate((prev) => prev + 1);
  };

  // useEffect to handle socket events and initialize the player
  useEffect(() => {
    const id = prompt("Enter your player id (player1 or player2):", "player1");
    if (!id) {
      alert("Player id is required!");
      return;
    }
    setPlayerId(id);
    socket.emit("join_game", { player: id });

    socket.on("update_game", (data) => {
      if (data.error) {
        alert(data.error);
      } else {
        setDeckSize(data.deck_size || 0);
        setPlayerTurn(data.turn || "");
        setPending(data.pending || null);
        if (data.hand !== undefined && data.hand !== null) {
          setMyHand(data.hand);
        }
        if (data.scores) {
          setScores(data.scores);
        }
        setDiscardString(data.discard_string || null);
        setIsDrawing(false); // Reset isDrawing when update is received

        if (data.message && data.message.toLowerCase().includes("new round started")) {
          setMessage("");
          setRoundFinished(false);
          setGameOver(false);
        } else if (data.message) {
          setMessage(data.message);
          if (data.message.toLowerCase().includes("round")) {
            setRoundFinished(false);
          }
        }
      }
    });

    socket.on("round_over", (data) => {
      setMessage(`${data.winner} won this round! Reason: ${data.reason}, Points: ${data.points}`);
      setGameOver(false);
      setRoundFinished(false);
    });

    socket.on("game_over", (data) => {
      if (data.score !== undefined) {
        setMessage(`${data.winner} reached 100! Final Score: ${data.score}`);
      } else {
        setMessage(`${data.winner} won! Reason: ${data.reason}, Points: ${data.points}`);
      }
      setGameOver(true);
      setRoundFinished(true);
    });

    socket.on("knock_error", (data) => {
      alert(data.error);
    });
    
    return () => {
      socket.off("update_game");
      socket.off("round_over");
      socket.off("game_over");
      socket.off("knock_error");
    };
  }, [socket]);

  // Handler for drawing a card from the stock pile
  const handleDrawFromStock = () => {
    if (isDrawing) return; // Block if already drawing
    setIsDrawing(true);
    socket.emit("draw_card", { player: playerId, source: "stock" });
    forceUpdate();
  };

  // Handler for drawing a card from the discard pile
  const handleTakeDiscard = () => {
    if (isDrawing) return;
    setIsDrawing(true);
    socket.emit("draw_card", { player: playerId, source: "discard" });
    forceUpdate();
  };

  // Handler for discarding a card; cardIndex indicates which card is being discarded
  const handleDiscardCard = (cardIndex) => {
    socket.emit("discard_card", { player: playerId, cardIndex });
    forceUpdate();
  };

  // Handler for the knock action
  const handleKnock = () => {
    socket.emit("knock", { player: playerId });
    forceUpdate();
  };

  // Handler for starting the next round
  const handleNextRound = () => {
    socket.emit("new_round");
    setMessage("");
    setMyHand([]);
    setGameOver(false);
    setRoundFinished(true);
  };

  // Handler for starting a completely new game
  const handleNewGame = () => {
    socket.emit("new_game");
    setMessage("");
    setMyHand([]);
    setGameOver(false);
    setRoundFinished(false);
  };

  return (
    <div className="board-container" style={{ fontFamily: "'Montserrat', sans-serif" }}>
      {/* Display the current scores */}
      <div className="score-board">
        <h3>Scores</h3>
        <p>Player 1: {scores.player1} | Player 2: {scores.player2}</p>
      </div>
      
      {/* Display the stock and discard piles */}
      <div className="stock-discard-row">
        <div className="stock-pile">
          {deckSize > 0 ? (
            <img
              src="/images/my-card-back.png"
              alt="Stock Pile"
              className="stock-card-back"
            />
          ) : (
            <div className="empty-stock">Empty</div>
          )}
          <p>({deckSize} cards)</p>
        </div>
        <div className="discard-pile">
          {discardString ? (
            <Card
              cardText={discardString}
              style={{ width: "90px", height: "140px", margin: "0 auto" }}
            />
          ) : (
            <div
              style={{
                width: "90px",
                height: "140px",
                border: "1px solid black",
                borderRadius: "8px"
              }}
            />
          )}
          <p>Discard</p>
        </div>
      </div>

      {/* Display the current turn */}
      <h3>Current Turn: {playerTurn}</h3>
      {pending === playerId && myHand.length !== 11 ? (
        <p>Please click on a card in your hand to discard.</p>
      ) : (
        <div className="draw-buttons">
          <button className="draw-button" onClick={handleDrawFromStock}>
            Draw from Stock
          </button>
          <button className="draw-button" onClick={handleTakeDiscard}>
            Take Discard
          </button>
          <button className="draw-button" onClick={handleKnock}>
            Knock
          </button>
        </div>
      )}

      {/* Render the player's hand */}
      <div className="players">
        <Player
          name={playerId}
          hand={myHand}
          onCardClick={pending === playerId ? handleDiscardCard : undefined}
        />
      </div>
      
      {/* Display game messages */}
      {message && <p className="game-message">{message}</p>}

      {/* Control buttons for round and game management */}
      <div className="round-controls">
        {message.toLowerCase().includes("round") && !gameOver && !roundFinished && (
          <button className="draw-button" onClick={handleNextRound}>
            Next Round
          </button>
        )}
        <button className="draw-button" onClick={handleNewGame}>
          New Game
        </button>
      </div>
    </div>
  );
}

export default Board;
