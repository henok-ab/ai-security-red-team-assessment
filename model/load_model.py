import torch

from model import SimpleCNN


MODEL_PATH = "model/weights/pytorch_model.bin"


model = SimpleCNN()

state_dict = torch.load(
    MODEL_PATH,
    map_location="cpu"
)


print("Loading model state dict...")

model.load_state_dict(state_dict)

print("Model state dict loaded successfully!")

model.eval()

print("Model loaded successfully!")