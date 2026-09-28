import torch
import torch.nn.functional as F
from torchvision import datasets, transforms
from PIL import Image

from model import SimpleCNN


# -----------------------------
# Configuration
# -----------------------------
EPSILON = 0.03 
ALPHA = 0.005 
STEPS = 10

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASS_NAMES = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]


# -----------------------------
# Load model
# -----------------------------
model = SimpleCNN().to(DEVICE)

model.load_state_dict(
    torch.load(
        "model/weights/pytorch_model.bin",
        map_location=DEVICE
    )
)

model.eval()


# -----------------------------
# CIFAR-10 preprocessing
# -----------------------------
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2023, 0.1994, 0.2010)
    )
])


# -----------------------------
# Load CIFAR-10 test dataset
# -----------------------------
dataset = datasets.CIFAR10(
    root="./data",
    train=False,
    download=True,
    transform=transform
)


# -----------------------------
# PGD Attack
# -----------------------------
def pgd_attack(model, image, label, epsilon, alpha, steps):

    original_image = image.clone().detach()

    adversarial_image = image.clone().detach()

    for _ in range(steps):

        adversarial_image.requires_grad = True

        output = model(adversarial_image)

        loss = F.cross_entropy(output, label)

        model.zero_grad()

        loss.backward()

        gradient = adversarial_image.grad.sign()

        # Move in the direction that increases the loss
        adversarial_image = adversarial_image.detach() + alpha * gradient

        # Keep perturbation inside epsilon
        perturbation = torch.clamp(
            adversarial_image - original_image,
            min=-epsilon,
            max=epsilon
        )

        adversarial_image = original_image + perturbation

    return adversarial_image.detach()


# -----------------------------
# Find a successful attack
# -----------------------------
for index in range(len(dataset)):

    image, label = dataset[index]

    image = image.unsqueeze(0).to(DEVICE)
    label_tensor = torch.tensor([label]).to(DEVICE)

    # Clean prediction
    with torch.no_grad():
        clean_output = model(image)
        clean_prediction = clean_output.argmax(dim=1).item()

    # Only attack correctly classified images
    if clean_prediction != label:
        continue

    # Generate PGD adversarial image
    adversarial_image = pgd_attack(
        model,
        image,
        label_tensor,
        EPSILON,
        ALPHA,
        STEPS
    )

    # Adversarial prediction
    with torch.no_grad():
        adversarial_output = model(adversarial_image)

        adversarial_prediction = (
            adversarial_output.argmax(dim=1).item()
        )

        adversarial_probability = (
            torch.softmax(adversarial_output, dim=1)
            .max()
            .item()
        )

    # Check whether attack succeeded
    success = adversarial_prediction != label

    if success:

        print("----- PGD Attack -----")
        print(f"Image index: {index}")
        print(f"True label: {CLASS_NAMES[label]}")
        print(f"Clean prediction: {CLASS_NAMES[clean_prediction]}")
        print(
            f"Adversarial prediction: "
            f"{CLASS_NAMES[adversarial_prediction]}"
        )
        print(f"Adversarial confidence: {adversarial_probability:.4f}")
        print(f"Epsilon: {EPSILON}")
        print(f"Alpha: {ALPHA}")
        print(f"Steps: {STEPS}")
        print(f"Attack successful: {success}")

        # Convert normalized tensor back to image
        mean = torch.tensor(
            [0.4914, 0.4822, 0.4465],
            device=DEVICE
        ).view(1, 3, 1, 1)

        std = torch.tensor(
            [0.2023, 0.1994, 0.2010],
            device=DEVICE
        ).view(1, 3, 1, 1)

        clean_display = image * std + mean
        adversarial_display = adversarial_image * std + mean

        clean_display = torch.clamp(clean_display, 0, 1)
        adversarial_display = torch.clamp(adversarial_display, 0, 1)

        clean_display = (
            clean_display.squeeze(0)
            .permute(1, 2, 0)
            .cpu()
            .numpy()
        )

        adversarial_display = (
            adversarial_display.squeeze(0)
            .permute(1, 2, 0)
            .cpu()
            .numpy()
        )

        # Save images
        Image.fromarray(
            (clean_display * 255).astype("uint8")
        ).save(
            "results/adversarial/pgd_clean.png"
        )

        Image.fromarray(
            (adversarial_display * 255).astype("uint8")
        ).save(
            "results/adversarial/pgd_adversarial.png"
        )

        print("Clean image saved:")
        print("results/adversarial/pgd_clean.png")

        print("Adversarial image saved:")
        print("results/adversarial/pgd_adversarial.png")

        break

