import torch

MODEL_PATH = "model/weights/pytorch_model.bin"

state_dict = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

print("Type:", type(state_dict))
print("\nModel parameters:")

for name, tensor in state_dict.items():
    print(f"{name:30} {tuple(tensor.shape)}")