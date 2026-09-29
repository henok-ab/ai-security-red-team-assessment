import torch

MODEL_PATH = "model/weights/pytorch_model.bin"

state_dict = torch.load(
    MODEL_PATH,
    map_location="cpu"
)  

print("Type:", type(state_dict))
print("\nModel parameters:")

for name, tensor in state_dict.items():// tensor is a PyTorch tensor representing the weights or biases of a layer in the model. The name is a string that identifies the parameter (e.g., "conv1.weight" for the weights of the first convolutional layer).
    print(f"{name:30} {tuple(tensor.shape)}")  //tensor.shape returns the shape of the tensor as a tuple, which is then formatted and printed alongside the parameter name.