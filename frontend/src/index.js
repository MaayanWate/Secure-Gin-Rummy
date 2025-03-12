import React from "react";
import ReactDOM from "react-dom";
import App from "./App";

// Render the main App component within React.StrictMode for highlighting potential problems
// The App component is mounted to the DOM element with id "root"
ReactDOM.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
    document.getElementById("root")
);
