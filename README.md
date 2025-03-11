# Secure Gin Rummy - Setup Instructions

## 📌 Project Overview  
This project implements a secure version of Gin Rummy using cryptographic techniques such as ElGamal encryption and Zero Knowledge Proofs (ZKP) for verifying shuffles and valid moves without revealing card details.  

## 🦜 Prerequisites  
Before setting up the project, ensure you have the following installed:  
- Python 3.8+ (for backend)  
- Node.js & npm (for frontend)  
- Virtual environment (optional but recommended for Python dependencies)  

## 🚀 Backend Setup (Flask Server)  

### 1️⃣ Install dependencies  
sh
cd backend
python -m venv venv  # Optional: Create a virtual environment
source venv/bin/activate  # On Windows use 'venv\Scripts\activate'
pip install -r requirements.txt  # Install dependencies
  

### 2️⃣ Run the Flask server  
sh
python app.py
  
By default, the server runs on [http://localhost:5000](http://localhost:5000).  

### 3️⃣ Verify the server is running  
Open your browser or use Postman to check:  

GET http://localhost:5000/start_game
  
Expected response:  
json
{"message": "Game started!"}
  

---

## 🎨 Frontend Setup (React Client)  

### 1️⃣ Install dependencies  
sh
cd frontend
npm install
  

### 2️⃣ Start the React application  
sh
npm start
  
The frontend should run on [http://localhost:3000](http://localhost:3000).  

### 3️⃣ Open the game  
Go to [http://localhost:3000](http://localhost:3000) in your browser and enter your player ID (player1/player2) when prompted.  

---

## 🎲 Playing the Game  
To play the game, you'll need *two players*, each using a separate browser window:  

1. *Open two browser windows:*  
   - One in a *regular browser window*.  
   - One in an *incognito (private) mode*.  

2. *Go to the game URL:*  
   - Open http://localhost:3000 in both windows.  

3. *Enter player IDs:*  
   - In one window, enter "player1".  
   - In the second window, enter "player2".  

4. *Start playing!*  
   - Players can draw, discard, and knock according to the rules of Gin Rummy.  
   - The game state is synchronized between both players via WebSockets.  

---

## 🤦🏽‍♂️ Troubleshooting  

### ⚠️ Backend Issues  
1. ModuleNotFoundError  
   - Ensure you're in the backend folder and the virtual environment is activated.  
   - Run pip install -r requirements.txt again.  

2. Address already in use (OSError)  
   - Kill any running Flask processes:  
   sh
   lsof -i :5000  # Find process using port 5000
   kill -9 <PID>   # Replace <PID> with the actual process ID
     

### ⚠️ Frontend Issues  
1. react-scripts not found  
   - Run npm install again in the frontend directory.  

2. Page not updating after button click  
   - Try refreshing the page (Ctrl+R or Cmd+R).  
   - Check the browser console (F12 > Console) for errors.  

---

## 📌 Next Steps  
- Ensure all Zero Knowledge Proofs (ZKP) are correctly validating the game logic.  
- Fix the double-click issue on game actions.  
- Finalize the UI for better card visibility.  

---
### ✅ You're Ready to Play Secure Gin Rummy! 🃏
