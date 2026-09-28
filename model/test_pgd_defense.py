import torch
from torchvision import datasets, transforms
from model import SimpleCNN


# -----------------------------------
# Configuration
# -----------------------------------

MODEL_PATH = "model/weights/pgd_defended_model.pth"

EPSILON = 0.03
ALPHA = 0.005
PGD_STEPS = 10


# -----------------------------------
# CIFAR-10 preprocessing
# -----------------------------------

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2470, 0.2435, 0.2616)
    )
])


# -----------------------------------
# Load model
# -----------------------------------

model = SimpleCNN()

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location="cpu"
    )
)

model.eval()


# -----------------------------------
# Load CIFAR-10 test image
# -----------------------------------

dataset = datasets.CIFAR10(
    root="./data",
    train=False,
    download=True,
    transform=transform
)

image, label = dataset[0]

image = image.unsqueeze(0)
label = torch.tensor([label])


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


# -----------------------------------
# Clean prediction
# -----------------------------------

with torch.no_grad():

    output = model(image)

    clean_prediction = output.argmax(dim=1).item()

print("----- PGD Defense Test -----")
print(f"True label: {classes[label.item()]}")
print(f"Clean prediction: {classes[clean_prediction]}")


# -----------------------------------
# PGD attack
# -----------------------------------

original_image = image.clone()
adversarial_image = image.clone()

for step in range(PGD_STEPS):

    adversarial_image.requires_grad = True

    output = model(adversarial_image)

    loss = torch.nn.functional.cross_entropy(
        output,
        label
    )

    model.zero_grad()

    loss.backward()

    gradient = adversarial_image.grad.data

    adversarial_image = (
        adversarial_image.detach()
        + ALPHA * gradient.sign()
    )

    # Keep perturbation within epsilon
    perturbation = (
        adversarial_image - original_image
    )

    perturbation = torch.clamp(
        perturbation,
        -EPSILON,
        EPSILON
    )

    adversarial_image = (
        original_image + perturbation
    )

    adversarial_image = torch.clamp(
        adversarial_image,
        -3,
        3
    )


# -----------------------------------
# Adversarial prediction
# -----------------------------------

with torch.no_grad():

    output = model(adversarial_image)

    adversarial_prediction = output.argmax(
        dim=1
    ).item()

    confidence = torch.softmax(
        output,
        dim=1
    )[0, adversarial_prediction].item()


# -----------------------------------
# Result
# -----------------------------------

print(f"PGD prediction: {classes[adversarial_prediction]}")
print(f"Confidence: {confidence:.4f}")
print(f"Epsilon: {EPSILON}")
print(f"Alpha: {ALPHA}")
print(f"Steps: {PGD_STEPS}")

if adversarial_prediction != label.item():

    print("Attack successful: True")
    print("Defense result: PGD attack still fooled the model")

else:

    print("Attack successful: False")
    print("Defense result: Model resisted the PGD attack")
