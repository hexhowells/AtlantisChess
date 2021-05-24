import chess
import Architectures.ResNet as ValueNetwork
from bitboard import BitBoard as bb
import torch
import numpy as np
from torch import nn
from matplotlib import pyplot as plt
import random


def moving_average(x, N=100):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)


def read_lines():
	with open("data/lichess.csv", "r") as fp:
		for line in fp:
			yield line[:-1]


def process_board(board):
	board_tensor = bb.serialise(board)
	#board_tensor = bb.split_channels(board_array)
	return board_tensor


def shuffle(x, y):
	indicies = np.arange(len(y))
	np.random.shuffle(indicies)

	a = x[indicies]
	b = y[indicies]

	return a, b


def process_game(game):
	x_batch, y_batch = [], []
	result, moves = game.split(',')
	target = 1 if result == "white" else -1
	
	board = chess.Board()

	x_batch.append(process_board(board))
	y_batch.append([target])
	y_batch = [[target]] * moves.count(' ')

	# Simulate the game given the list of moves
	for move in moves[:-1].split(' '):
		board.push_san(move)
		x_batch.append(process_board(board))

	return x_batch, y_batch



def get_batch(batch_size):
	x_batch, y_batch = [], []

	for i, game in enumerate(read_lines(), 1):
		board_tensors, targets = process_game(game)
		for idx in range(len(targets)):
			x_batch.append(board_tensors[idx])
			y_batch.append(targets[idx])

		# after 4000 games have been processed
		if (i % 4000) == 0:
			x_batch, y_batch = shuffle(np.asarray(x_batch), np.asarray(y_batch))
			_x_batch, _y_batch = [], []
			for j in range(len(y_batch)):
				_x_batch.append(x_batch[j])
				_y_batch.append(y_batch[j])

				if len(_y_batch) == batch_size:
					yield np.asarray(_x_batch), np.asarray(_y_batch)
					_x_batch, _y_batch = [], []

			x_batch, y_batch = [], []



# Initalise Model and Loss
model = ValueNetwork.ChessModel().cuda()
lossfn = nn.MSELoss()
losses = []

# Hyperparameters
batch_size = 256
lr = 1e-3
opt = torch.optim.Adam(params=model.parameters(), lr=lr)


# Training
for i in range(1):
	batch_count = 1
	print("Epoch: {}".format(i))
	for x_batch, y_batch in get_batch(batch_size):
		if (batch_count % 4000) == 0:
			print("\tProcessed {} batches".format(batch_count))
			plt.plot(moving_average(losses, 5000))
			plt.savefig("loss_inter.png")

		if (batch_count % 200_000) == 0: break  # stop training after roughly 50M board positions
			
		batch_count += 1
		opt.zero_grad()

		x_batch = torch.from_numpy(x_batch)
		y_batch = torch.from_numpy(y_batch)

		pred = model(x_batch.to(device="cuda", dtype=torch.float))
		
		loss = lossfn(pred, y_batch.type(torch.float))
		losses.append(loss.detach())
		loss.backward()
		opt.step()

	plt.plot(moving_average(losses, 5000))
	plt.savefig("loss_epoch_{}.png".format(i))
	#torch.save(model.state_dict(), "Models/Model_{}.pth".format(i))


# Plot the losses over the course of training
plt.plot(moving_average(losses, 5000))
plt.show()

# Save the trained model
torch.save(model.state_dict(), "Models/SmallModelDyn.pth")
print("Model Saved!")
