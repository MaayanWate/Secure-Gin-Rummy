import React from "react";
import io from "socket.io-client";
import Board from "./Board";
import "./styles.css";

// Create a socket connection to the backend server at localhost:5000
export const socket = io("http://localhost:5000");

// Main App component that renders the entire application
function App() {
  return (
    <div className="app-container">
      {/* Title of the game with the "title" CSS class for styling */}
      <h1 className="title">Gin Rummy</h1>
      
      {/* Render the Board component, passing the socket connection as a prop */}
      <Board socket={socket} />
    </div>
  );
}

export default App;
