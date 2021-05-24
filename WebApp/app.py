from flask import Flask, render_template, request, jsonify
import chess
from chess import Move
from random import randint
import sys
sys.path.insert(0,'..')
import engine

board = chess.Board()
prev_state = board
app = Flask(__name__, static_url_path='')


@app.route('/')
def index():
	global board
	board = chess.Board()
	return render_template("index.html")


@app.route('/fen', methods=['POST'])
def show_fen():
	fen_str = request.form['fen_str']
	print(fen_str)
	resp = jsonify(success=True)
	return resp


@app.route('/legal', methods=['POST'])
def is_legal():
	global board
	move = request.form['move_uci']
	if Move.from_uci(move) in board.legal_moves:
		resp = jsonify(legal=True, success=True)
	else:
		resp = jsonify(legal=False, success=True)

	return resp


@app.route('/move', methods=['POST'])
def make_move():
	global board
	move = request.form['move_uci']
	if Move.from_uci(move) in board.legal_moves:
		board.push(Move.from_uci(move))
		print(board.fen())
		move = engine.make_move(board)
		if move:
			board.push(move)
			print(board.fen())

		resp = jsonify(fen=board.fen(), legal=True, success=True)
	else:
		resp = jsonify(fen=board.fen(), legal=False, success=True)
	
	return resp

@app.route('/state', methods=['POST'])
def update_state():
	global board
	fen_str = request.form['fen_str']
	board = chess.Board(fen_str)
	
	return jsonify(success=True)



if __name__ == '__main__':
    app.run(port=5000,debug=True)