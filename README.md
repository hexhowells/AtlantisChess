<p align="center">
  <img src="https://github.com/hexhowells/AtlantisChess/blob/main/Logo.png" width=80%>
</p>


Neural network based chess engine, uses ResNet Value Network, AlphaBeta pruning, and Quiescence search

Features
-----
- Probably around 1100 ELO
- Uses a CNN (4 Residual Blocks) and material evaluation as a value function for AlphaBeta pruning
- Network trained on 50M+ board positions
- Uses a opening book for the first 4 moves
- Quiescence search used to reduce the horizon problem
- Player turn indicator on the UI
- Ability to rewind the game to see move history
- Ability to enable free play which allows pieces to be moved without actually playing them (easier for potential move visualisation)
- Can load board positions from FEN strings, this feature wasnt implimented in the UI and needs to be done in the browser console.

Data
-----
The value network was trained on ~50M board positions from the Lichess Open Database - https://database.lichess.org/

Usage
-----
Run ```WebApp/app.py``` and navigate to ```localhost:5000```. Refresh the page to start a new game.

Can use the forward and back buttons to navigate through the move history, home button takes you back to the current board position, only available if its the player's turn. Free play button allows pieces to be moved without actually playing them, this can be used for move visualisation when planning a move.

Statistics about the engine's move can be seen in the console.

Can run ```Tools/OpeningBook.py -create``` with a downloaded lichess dataset to create a larger opening book.

File Structure
-----
#### UI
- ```app.py``` - runs the server for the UI
- ```index.html``` - main page for playing chess
- ```chess.js``` - adds functionality to the chess board
#### Engine
- ```train.py``` - trains the value network
- ```train_dynamic.py``` - processes the data on the fly whilst training (slow but can handle larger datasets)
- ```bitboard.py``` - converts the chess board into a tensor for network ingestion
- ```engine.py``` - uses the trained network to process and play chess games
- ```hyperparameters.py``` - stores all the parameters for training and running the engine
- ```pre-process_data.py``` - may not be included in the public repo
- ```/Architectures``` - defines the network architectures
- ```/Models``` - stores the trained models
- ```/Data``` - stores the raw and processed training data and labels
- ```/Tools``` - tool to create and use the opening book
