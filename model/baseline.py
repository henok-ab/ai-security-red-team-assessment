import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

from model import SimpleCNN


# -------------------------
# 1. Model
# -------------------------

MODEL_PATH = "model/weights/pytorch_model.bin"

model = SimpleCNN()

state_dict = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

model.load_state_dict(state_dict)
model.eval()


# -------------------------
# 2. CIFAR-10 dataset
# -------------------------

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2023, 0.1994, 0.2010)
    )
])

test_dataset = datasets.CIFAR10(
    root="data",
    train=False,
    download=True,
    transform=transform
)

test_loader = DataLoader(
    test_dataset,
    batch_size=32,
    shuffle=False
)


# -------------------------
# 3. CIFAR-10 classes
# -------------------------

classes = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck"
]


# -------------------------
# 4. Test the model
# -------------------------

correct = 0
total = 0

with torch.no_grad():

    for images, labels in test_loader:

        outputs = model(images)

        predictions = torch.argmax(outputs, dim=1)

        total += labels.size(0)

        correct += (predictions == labels).sum().item()


# -------------------------
# 5. Calculate accuracy
# -------------------------

accuracy = 100 * correct / total

print(f"Test accuracy: {accuracy:.2f}%")