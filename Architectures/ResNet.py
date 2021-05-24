import torch
from torch import nn
import numpy as np
from torch.nn import functional as F

device = torch.device("cuda")# if torch.cuda.is_available() else torch.devce("cpu")
torch.set_default_tensor_type("torch.cuda.FloatTensor")

class ChessModel(torch.nn.Module):
	def __init__(self):
		super(ChessModel, self).__init__()

		self.a1 = nn.Conv2d(6, 256, kernel_size=3, padding=1).to(device)
		self.a_bat = nn.BatchNorm2d(256).to(device)

		self.b1 = nn.Conv2d(256, 256, kernel_size=3, padding=1).to(device)
		self.b2 = nn.Conv2d(256, 256, kernel_size=3, padding=1).to(device)
		self.b_bat = nn.BatchNorm2d(256).to(device)

		self.c1 = nn.Conv2d(256, 256, kernel_size=3, padding=1).to(device)
		self.c2 = nn.Conv2d(256, 256, kernel_size=3, padding=1).to(device)
		self.c_bat = nn.BatchNorm2d(256).to(device)

		self.d1 = nn.Conv2d(256, 256, kernel_size=3, padding=1).to(device)
		self.d2 = nn.Conv2d(256, 256, kernel_size=3, padding=1).to(device)
		self.d_bat = nn.BatchNorm2d(256).to(device)

		self.e1 = nn.Conv2d(256, 256, kernel_size=3, padding=1).to(device)
		self.e2 = nn.Conv2d(256, 256, kernel_size=3, padding=1).to(device)
		self.e_bat = nn.BatchNorm2d(256).to(device)

		self.f1 = nn.Conv2d(256, 4, kernel_size=1).to(device)
		self.f_bat = nn.BatchNorm2d(4).to(device)

		self.linear1 = nn.Linear(256, 256).to(device)
		self.linear2 = nn.Linear(256, 1).to(device)


	def forward(self, x):
		x.to(device)

		x = F.relu(self.a1(x))
		x_res = F.relu(self.a_bat(x))

		x = F.relu(self.b1(x_res))
		x = F.relu(self.b2(x))
		x = self.b_bat(x)
		x_res = F.relu(x.add(x_res))

		x = F.relu(self.c1(x_res))
		x = F.relu(self.c2(x))
		x = self.c_bat(x)
		x_res = F.relu(x.add(x_res))

		x = F.relu(self.d1(x_res))
		x = F.relu(self.d2(x))
		x = self.d_bat(x)
		x_res = F.relu(x.add(x_res))

		x = F.relu(self.e1(x_res))
		x = F.relu(self.e2(x))
		x = self.e_bat(x)
		x_res = F.relu(x.add(x_res))

		x = F.relu(self.f1(x_res))
		x = F.relu(self.f_bat(x))

		x = x.view(-1, 256)  # flatten

		x = torch.tanh(self.linear1(x))
		x = torch.tanh(self.linear2(x))

		return x.to(device='cpu')
