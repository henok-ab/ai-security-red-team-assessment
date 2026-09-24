import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

from model import SimpleCNN


MODEL_PATH = "model/weights/pytorch_model.bin"

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


def evaluate(transform, name):

    model = SimpleCNN()

    state_dict = torch.load(
        MODEL_PATH,
        map_location="cpu"
    )

    model.load_state_dict(state_dict)
    model.eval()

    dataset = datasets.CIFAR10(
        root="data",
        train=False,
        download=True,
        transform=transform
    )

    loader = DataLoader(
        dataset,
        batch_size=64,
        shuffle=False
    )

    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in loader:

            outputs = model(images)

            predictions = torch.argmax(
                outputs,
                dim=1
            )

            total += labels.size(0)

            correct += (
                predictions == labels
            ).sum().item()

    accuracy = 100 * correct / total

    print(f"{name}: {accuracy:.2f}%")


# 1. No normalization
evaluate(
    transforms.ToTensor(),
    "ToTensor only"
)


# 2. Standard CIFAR-10 normalization
# normalize the images using the mean and standard deviation of the CIFAR-10 dataset
#means = (0.4914, 0.4822, 0.4465) indicates the mean of the RGB channels
#stds = (0.2023, 0.1994, 0.2010) indicates the standard deviation of the RGB channels
evaluate(
    transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(
            (0.4914, 0.4822, 0.4465),
            (0.2023, 0.1994, 0.2010)
        )
    ]),
    "Standard CIFAR-10 normalization"
)