from bitboard import BitBoard as bb
import chess
import numpy as np


def read_file(filepath):
	with open(filepath, "r") as infile:
		clean_data = infile.read()

	return clean_data


def process_board(board, player):
	board_tensor = bb.serialise(board)
	return board_tensor


def shuffle(arry1, arry2):
	indicies = np.arange(len(arry2))
	np.random.shuffle(indicies)

	a = np.asarray(arry1)[indicies]
	b = np.asarray(arry2)[indicies]

	return a, b


def main():
	filepath = "Data/lichess.csv"
	game_data = []
	target_data = []

	clean_data = read_file(filepath)

	print("Number of Games: {:,}".format(len(clean_data.split('\n'))))

	# Iterate through each game in the dataset
	for i, game in enumerate(clean_data.split('\n')):
		if (i % 100) == 0:
			print("Processing Game: {}\tGame Boards: {}".format(i, len(target_data)))

		# Stop after so many games have been processed (smaller data allows for quicker testing)
		if i > 40_000:#17500:
			break

		# Initialisation
		winner, moves = game.split(',')
		board = chess.Board()	

		player = 'B'
		target = 1 if winner == 'white' else -1

		# Push inital Move
		board_tensor = process_board(board, player='W')
		game_data.append(board_tensor)
		target_data.append(target)

		# Simulate the game given the list of moves
		for move in moves[:-1].split(' '):
			board.push_san(move)
			board_tensor = process_board(board, player=player)
			game_data.append(board_tensor)
			target_data.append(target)


	print("Final Game Data Shape: {}".format(np.asarray(game_data).shape))
	print("Final Target Data Shape: {}".format(np.asarray(target_data).shape))

	a, b = shuffle(game_data, target_data)

	print("Saving Data...")
	np.save("Data/Boards2.npy", a)
	np.save("Data/Targets2.npy", b)


if __name__ == "__main__":
	main()

