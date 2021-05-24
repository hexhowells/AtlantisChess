var canMove = true;
var boards = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"]
var board_ptr = 0
var free_play = false;
var fen = null;


function game_stack_add(board) {
	if (boards[boards.length-1] !== board.fen())
		boards.push(board.fen());
	board_ptr = boards.length - 1;
}

function freePlay(){
	console.log("free play")
	if (free_play){
		free_play = false;
		console.log("boards list:")
		console.log(boards)
		updateBoard(boards[boards.length-1]);
		document.getElementById("freePlayBtn").innerHTML = "Free Play: <b>OFF</b>";
	}
	else {
		free_play = true;
		document.getElementById("freePlayBtn").innerHTML = "Free Play: <b>ON</b>";
	}
}


function onDrop (source, target, piece, newPos, oldPos, orientation) {
	if (free_play)
		return;

	canMove = false;

	// Update the player move indicator
	document.getElementById("atlantis-indicator").style.color = "black";
	document.getElementById("player-indicator").style.color = "#cccccc";

	isPromotion(piece, target);

	// Send move uci string to the server via an asynchronous POST request
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		console.log(`Status: ${this.status}`);
	  if (this.readyState == 4 && this.status == 200) {
	   var resp = JSON.parse(this.responseText);
	   console.log(resp);

	   game_stack_add(board);
	   updateBoard(resp.fen);
	   game_stack_add(board);

	   document.getElementById("atlantis-indicator").style.color = "#cccccc";
	   document.getElementById("player-indicator").style.color = "black";
	   canMove = true;
	  }
	};
	xhttp.open("POST", "/move");
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.send(`move_uci=${source+target}`);
}


function isPromotion (piece, target) {
	console.log("Promotion");
	if (piece[1] == 'P' && target[1] == '8') {
		window.alert("Pawn Premotion Detected!");
	}
}


function declareWinner (winner) {
	if (winner == "player")
		window.alert("Game Result: Player Wins.");
	else if (winner == "atlantis")
		window.alert("Game Result: Atlantis Wins.");
	else
		window.alert("Game Result: Draw.");
}


function onDragStart (source, piece, position, orientation) {
	if (free_play)
		return true
	if (board_ptr !== boards.length - 1)
		return false
	if (piece.substring(0,1) == 'b') 
		return false;
	else if (canMove)
		return true;
	else
		return false;
}


function getFen() {
	console.log(board.fen());
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		console.log(`Status: ${this.status}`);
	  if (this.readyState == 4 && this.status == 200) {
	   var resp = JSON.parse(this.responseText);
	   console.log(resp.success);
	  }
	};
	xhttp.open("POST", "/fen");
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.send(`fen_str=${board.fen()}`);
}


function updateBoard(new_fen) {
	board.position(new_fen, useAnimation=true);
}


function rewindBoard(dir) {
	if (canMove) {
		if (dir == 'back' && board_ptr > 0) {
			board_ptr -= 1;
		}
		else if (dir == 'forward') {
			if ((board_ptr + 1) < boards.length)
				board_ptr += 1;
		}
		else if (dir == 'home') {
			board_ptr = boards.length - 1;
		}

		updateBoard(boards[board_ptr]);
	}	
}

function setBoard(fen) {
	var http = new XMLHttpRequest();
	http.open("POST", "/state");
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	http.send(`fen_str=${fen}`);
	updateBoard(fen);
	document.getElementById("atlantis-indicator").style.color = "#cccccc";
	document.getElementById("player-indicator").style.color = "black";
	canMove = true;
}