import React, { useEffect, useState } from "react";
import "./Card.css";

// ממיר את שם הסוג לסמל המתאים
function getSuitSymbol(suitName) {
  switch (suitName) {
    case "Hearts":
      return "♥";
    case "Diamonds":
      return "♦";
    case "Clubs":
      return "♣";
    case "Spades":
      return "♠";
    default:
      return suitName; // חלופה במקרה שהסוג לא ידוע
  }
}

// בודק אם הקלף אדום או שחור
function getColorClass(suitName) {
  return suitName === "Hearts" || suitName === "Diamonds" ? "red-card" : "black-card";
}

function Card({ cardText, style, onClick }) {
  // אנימציה של כניסה לקלף
  const [animate, setAnimate] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimate(false);
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  // מפצל את הטקסט (למשל "Hearts A")
  const text = String(cardText);
  const parts = text.split(" ");
  if (parts.length < 2) {
    return (
      <div className={`card ${animate ? "card-animate" : ""}`} style={style} onClick={onClick}>
        {text}
      </div>
    );
  }

  const suitName = parts[0];  // Hearts, Diamonds, Clubs, Spades
  const rankStr = parts[1];   // A, K, Q, J, Prince או מספר

  const suitSymbol = getSuitSymbol(suitName);
  const colorClass = getColorClass(suitName);

  // בודק אם הערך הוא מספר (למספרים 2 עד 10)
  let rankNum = parseInt(rankStr, 10);
  if (isNaN(rankNum)) {
    rankNum = -1;
  }

  // בונה את התוכן המרכזי של הקלף
  let centerContent;
  if (rankStr === "A") {
    // במקרה של אס, מוצג רק הסמל ולא האות "A"
    centerContent = (
      <div className="card-center-big">
        {suitSymbol}
      </div>
    );
  } else if (rankStr === "K") {
    centerContent = (
      <div className="card-center-big">
        <img src={`${process.env.PUBLIC_URL}/images/king.jpg`} alt="King" className="king-img" />
      </div>
    );
  } else if (rankStr === "Q") {
    centerContent = (
      <div className="card-center-big">
        <img src={`${process.env.PUBLIC_URL}/images/queen.png`} alt="Queen" className="queen-img" />
      </div>
    );
  } else if (rankStr === "J") {
    centerContent = (
      <div className="card-center-big">
        <img src={`${process.env.PUBLIC_URL}/images/prince.jpg`} alt="Prince" className="prince-img" />
      </div>
    );
  } else if (rankNum >= 2 && rankNum <= 10) {
    const suitsArray = [];
    for (let i = 0; i < rankNum; i++) {
      suitsArray.push(
        <div key={i} className="center-suit">
          {suitSymbol}
        </div>
      );
    }
    centerContent = <div className="card-center">{suitsArray}</div>;
  } else {
    centerContent = (
      <div className="card-center-big">
        {rankStr} {suitSymbol}
      </div>
    );
  }

  return (
    <div className={`card ${colorClass} ${animate ? "card-animate" : ""}`} style={style} onClick={onClick}>
      {/* פינות הקלף */}
      <div className="corner top-left">
        <div className="corner-rank">{rankStr}</div>
        <div className="corner-suit">{suitSymbol}</div>
      </div>
      <div className="corner top-right">
        <div className="corner-rank">{rankStr}</div>
        <div className="corner-suit">{suitSymbol}</div>
      </div>
      <div className="corner bottom-left">
        <div className="corner-rank">{rankStr}</div>
        <div className="corner-suit">{suitSymbol}</div>
      </div>
      <div className="corner bottom-right">
        <div className="corner-rank">{rankStr}</div>
        <div className="corner-suit">{suitSymbol}</div>
      </div>

      {/* תוכן מרכזי */}
      {centerContent}
    </div>
  );
}

export default Card;
