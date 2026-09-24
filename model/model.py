import torch.nn as nn


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(3, 32, 3)
        self.conv2 = nn.Conv2d(32, 64, 3)
        self.conv3 = nn.Conv2d(64, 128, 3)

        self.pool = nn.MaxPool2d(2, 2)

        self.fc1 = nn.Linear(2048, 512)
        self.fc2 = nn.Linear(512, 10)

    def forward(self, x):

        x = self.pool(nn.ReLU()(self.conv1(x)))

        x = self.pool(nn.ReLU()(self.conv2(x)))

        x = nn.ReLU()(self.conv3(x))

        x = x.view(x.size(0), -1)

        x = nn.ReLU()(self.fc1(x))

        x = self.fc2(x)

        return x