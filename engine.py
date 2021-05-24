import numpy as np
import torch

from bitboard import BitBoard as bb
import hyperparameters as hp

import Architectures.ResNet as ValueNetwork
#import Architectures.ResNetBig as ValueNetwork

import chess
import random
import json
import copy as cp


model = ValueNetwork.ChessModel().cuda()
model.load_state_dict(torch.load("../Models/ModelResLarge.pth"))

nodes = 0

with open("../Data/OpeningBook.json", 'r') as bookfile:
	book = json.load(bookfile)



def evaluate(board):
	material = count_material(board)
	board_tensor = torch.from_numpy(bb.serialise(board)).unsqueeze(dim=0)
	value = model(board_tensor.to(device="cuda", dtype=torch.float)).item()

	return value + material


def count_material(board):
	mat = {'.':0, 'p':0, 'r':0, 'n':0, 'b':0, 'q':0, 'k':0,
		  		  'P':0, 'R':0, 'N':0, 'B':0, 'Q':0, 'K':0}
	for piece in str(board).replace('\n', ' ').split(' '):
		mat[piece] += 1

	material_score = 	100 * (mat['K'] - mat['k']) + \
						0.9 * (mat['Q'] - mat['q']) + \
						0.5 * (mat['R'] - mat['r']) + \
						0.3 * ((mat['B'] - mat['b']) + (mat['N'] - mat['n'])) + \
						0.1 * (mat['P'] - mat['p'])

	return -material_score


def negamax(board, depth):
	global nodes
	nodes += 1
	if depth == 0:
		return evaluate(board)

	max_v = -1_000_000
	for move in board.legal_moves:
		board.push(move)
		score = -negamax(board, depth-1)
		board.pop()

		if score > max_v:
			max_v = score

	return max_v


def alphabeta(board, alpha, beta, depth):
	global nodes
	nodes += 1
	if depth == 0:
		return quiescence(board, alpha, beta, depth=hp.qsearch_depth)
		#return evaluate(board)

	for move in board.legal_moves:
		board.push(move)
		score = -alphabeta(board, -beta, -alpha, depth-1)
		board.pop()

		if score >= beta:
			return beta  # fail hard beta-cutoff

		if score > alpha:
			alpha = score

	return alpha


def quiescence(board, alpha, beta, depth):
	global nodes
	nodes += 1

	if nodes >= hp.node_limit: # if node limit reached
		return evaluate(board)

	if depth == 0:
		return evaluate(board)

	stand_pat = evaluate(board)

	if stand_pat >= beta:
		return beta
	if alpha < stand_pat:
		alpha = stand_pat

	all_moves = [x for x in board.legal_moves]

	for move in capturing_moves(board, all_moves):
		board.push(move)
		score = -quiescence(board, -beta, -alpha, depth-1)
		board.pop()

		if score >= beta:
			return beta
		if score > alpha:
			alpha = score

	return alpha


def capturing_moves(board, moves):
	capture_moves = []
	for move in moves:
		dest = str(move)[2:4]
		dest_piece = board.piece_at(chess.SQUARE_NAMES.index(dest))

		if dest_piece:  # if destination contains a piece
			capture_moves.append(move)

	return capture_moves


def make_move(board):
	global nodes
	nodes = 0

	moves = [x for x in board.legal_moves]

	if len(moves) == 0:
		print("Game Won by Player!")
		return None

	turn_count = int(board.fen().split(' ')[-1])

	if turn_count < hp.opening_book_lim+1:
		move = query_opening_book(board)
		if not move:
			print("\nNo move found with opening book, querying network...")
			move = query_network(board, moves)
	else:
		move = query_network(board, moves)

	return move


def query_network(board, moves):
	preds = get_move_values(board, moves)

	show_move_info(board, moves, preds)

	best_move = preds.index(sorted(preds)[0])
	move = moves[best_move]

	return move


def query_opening_book(board):
	player_move = ' '.join(get_move_stack(board))
	book_moves = search_book(player_move)
	if len(book_moves) > 0:
		chosen_move = choose_book_move(board, book_moves)
		if chosen_move:
			return chosen_move
	
	return None


def get_move_stack(board):
	uci_move_stack = cp.copy(board.move_stack)
	san_move_stack = []
	board.reset()

	for move in uci_move_stack:
		san_move_stack.append(board.san(move))
		board.push(move)

	return san_move_stack


def search_book(player_move):
	selected_moves = {}
	for moves, stats in book.items():
		p_len = len(player_move) + 1
		move_list = moves.split(' ')
		p_move_list = player_move.split(' ')

		if player_move in moves[:p_len] and len(move_list) == len(p_move_list)+1:
			selected_moves[moves] = stats

	return sort_popularity(selected_moves)


def sort_popularity(book):
	return dict(sorted(book.items(), key=lambda item: item[1][3], reverse=True))


def choose_book_move(board, book_moves):
	best_moves = []
	for i, (move, stats) in enumerate(book_moves.items()):
		if i >= 5: break
		if stats[2] == 0: break
		best_moves.append(move)

	if len(best_moves) == 0:
		return None

	max_idx = len(best_moves) - 1
	chosen_move = best_moves[random.randint(0, max_idx)].split(' ')[-1]
	return board.parse_san(chosen_move)


def get_move_values(board, moves):
	preds = []
	for move in moves:
		board.push(move)
		val = alphabeta(board, -1_000_000, 1_000_000, depth=hp.search_depth)
		preds.append(val)
		board.pop()

	return preds


def show_move_info(board, all_moves, preds):
	print('-' * 20)

	print("\nMaterial Score: {}".format(-count_material(board)))
	print("\nExplored {:,} nodes".format(nodes))

	move_values = [x for x in zip([str(x) for x in all_moves], preds)]
	move_values.sort(key=lambda x: x[1])  # sort moves by best value for black

	print("\nAverage Score: {:.2f}".format((sum(preds) / len(preds))))

	print("\n###  Best 3 Moves:")
	[print(best_move) for best_move in move_values[:3]]

	print("\n###  Worst 3 Moves:")
	[print(worst_move) for worst_move in reversed(move_values[-3:])]

	print("\n###  All Moves")
	[print(move_value) for move_value in move_values]

	print('-' * 20)
