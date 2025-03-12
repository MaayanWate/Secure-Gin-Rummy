import React, { useEffect, useState } from "react";
import { socket } from "./App";
import Card from "./Card";
import "./styles.css";

function Player({ name, hand = [], onCardClick }) {
  // Initialize local state for the player's hand
  const [localHand, setLocalHand] = useState(hand);

  // Update localHand state when the hand prop changes
  useEffect(() => {
    setLocalHand(hand || []);
  }, [hand]);

  // Handle the drag start event, storing the index of the dragged card
  const handleDragStart = (e, fromIndex) => {
    e.dataTransfer.setData("fromIndex", fromIndex);
  };

  // Prevent default behavior to allow drop events
  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Handle the drop event to rearrange the cards
  const handleDrop = (e, toIndex) => {
    e.preventDefault();
    const fromIndex = parseInt(e.dataTransfer.getData("fromIndex"), 10);
    if (fromIndex === toIndex) return;
    const newHand = [...localHand];
    const [moved] = newHand.splice(fromIndex, 1);
    newHand.splice(toIndex, 0, moved);
    setLocalHand(newHand);
    socket.emit("new_hand", { player: name, toIndex: toIndex, fromIndex: fromIndex });
  };

  // If there are no cards in the hand, display a message
  if (!localHand || localHand.length === 0) {
    return (
      <div className="player-container">
        <h3>{name}</h3>
        <p>No cards in hand.</p>
      </div>
    );
  }

  return (
    <div className="player-container">
      <h3>{name}</h3>
      <div className="hand">
        {localHand.map((cardText, index) => {
          const total = localHand.length;
          // Fan out the cards in an arc: increasing angle and horizontal offset
          const angle = (index - (total - 1) / 2) * 15;
          const xOffset = (index - (total - 1) / 2) * 40;
          const absDistance = Math.abs(index - (total - 1) / 2);
          // The arc effect: center is raised and the sides are lower
          const yOffset = -absDistance * 8;
          return (
            <div
              key={index}
              draggable
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, index)}
              style={{
                position: "absolute",
                width: "90px",
                height: "140px",
                left: "50%",
                top: "50%",
                transformOrigin: "bottom center",
                transform: `
                  translate(-50%, -50%)
                  translate(${xOffset}px, ${yOffset}px)
                  rotate(${angle}deg)
                `,
                transition: "transform 0.3s",
              }}
              onClick={onCardClick ? () => onCardClick(index) : undefined}
            >
              <Card cardText={cardText} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Player;
