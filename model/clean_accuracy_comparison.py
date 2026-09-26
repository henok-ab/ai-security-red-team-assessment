import torch
from torchvision import datasets, transforms
from model import SimpleCNN


# -----------------------------------
# Configuration
# -----------------------------------

ORIGINAL_MODEL = "model/weights/pytorch_model.bin"
DEFENDED_MODEL = "model/weights/defended_model.pth"


# -----------------------------------
# Preprocessing
# -----------------------------------

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2470, 0.2435, 0.2616)
    )
])


# -----------------------------------
# Load CIFAR-10 test set
# -----------------------------------

test_dataset = datasets.CIFAR10(
    root="./data",
    train=False,
    download=True,
    transform=transform
)


# -----------------------------------
# Accuracy function
# -----------------------------------

def calculate_accuracy(model, model_name):

    correct = 0
    total = 0

    model.eval()

    with torch.no_grad():

        for image, label in test_dataset:

            image = image.unsqueeze(0)

            output = model(image)

            prediction = output.argmax(
                dim=1
            ).item()

            total += 1

            if prediction == label:
                correct += 1

    accuracy = (
        correct / total
    ) * 100

    print(f"\n----- {model_name} -----")
    print(f"Correct: {correct}/{total}")
    print(f"Clean Accuracy: {accuracy:.2f}%")


# -----------------------------------
# Load original model
# -----------------------------------

original_model = SimpleCNN()

original_model.load_state_dict(
    torch.load(
        ORIGINAL_MODEL,
        map_location="cpu"
    )
)


# -----------------------------------
# Load defended model
# -----------------------------------

defended_model = SimpleCNN()

defended_model.load_state_dict(
    torch.load(
        DEFENDED_MODEL,
        map_location="cpu"
    )
)


# -----------------------------------
# Compare
# -----------------------------------

print("===== CLEAN ACCURACY COMPARISON =====")

calculate_accuracy(
    original_model,
    "Original Model"
)

calculate_accuracy(
    defended_model,
    "Defended Model"
)

