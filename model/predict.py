import torch
from torchvision import datasets, transforms
from model import SimpleCNN


# -----------------------------
# 1. Load the trained model
# -----------------------------

MODEL_PATH = "model/weights/pytorch_model.bin"

model = SimpleCNN()

state_dict = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

model.load_state_dict(state_dict)
model.eval()


# -----------------------------
# 2. CIFAR-10 preprocessing
# -----------------------------

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2023, 0.1994, 0.2010)
    )
])


# -----------------------------
# 3. Load CIFAR-10 test data
# -----------------------------

test_dataset = datasets.CIFAR10(
    root="data",
    train=False,
    download=True,
    transform=transform
)


# -----------------------------
# 4. CIFAR-10 class names
# -----------------------------

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


# -----------------------------
# 5. Select one image
# -----------------------------

index = 0

image, true_label = test_dataset[index]


# -----------------------------
# 6. Make prediction
# -----------------------------

with torch.no_grad():

    # Add batch dimension
    image = image.unsqueeze(0)

    outputs = model(image)

    probabilities = torch.softmax(outputs, dim=1)

    predicted_label = torch.argmax(probabilities, dim=1).item()

    confidence = probabilities[0][predicted_label].item()


# -----------------------------
# 7. Display result
# -----------------------------

print("----- Prediction Result -----")

print(f"Image index: {index}")

print(f"True label: {classes[true_label]}")

print(f"Predicted: {classes[predicted_label]}")

print(f"Confidence: {confidence * 100:.2f}%")