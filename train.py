import Architectures.ResNet as ValueNetwork
from bitboard import BitBoard as bb
import torch
import numpy as np
from torch import nn
from matplotlib import pyplot as plt
import hyperparameters as hp


def moving_average(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)


# Load data
print("Loading data...")
board_tensors = np.load("Data/Boards2.npy")
targets = np.load("Data/Targets2.npy")

# Initalise Model and Loss
model = ValueNetwork.ChessModel().cuda()
lossfn = nn.MSELoss()
losses = [1]

# Hyperparameters
batch = hp.batch_size
lr = hp.lr
opt = torch.optim.Adam(params=model.parameters(), lr=lr)

board_count = board_tensors.shape[0]
print("Board Count: {:,}".format(board_count))


# Training
for i in range(5):
	print("Epoch: {}\tLoss: {}".format(i, losses[-1]))
	for idx in range(batch, board_count, batch):
		opt.zero_grad()

		board_tensor = torch.from_numpy(board_tensors[idx-batch:idx][:][:][:])
		target = torch.from_numpy(np.asarray(targets[idx-batch:idx])).unsqueeze(dim=1)

		pred = model(board_tensor.to(device="cuda", dtype=torch.float))
		
		loss = lossfn(pred, target.type(torch.float))
		losses.append(loss.detach())
		loss.backward()
		opt.step()


# Plot the losses over the course of training
plt.plot(moving_average(losses, 100))
plt.show()

# Save the trained model
torch.save(model.state_dict(), "Models/model.pth")
print("Model Saved!")
