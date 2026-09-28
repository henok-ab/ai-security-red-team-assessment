import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from model import SimpleCNN


# -----------------------------------
# Configuration
# -----------------------------------

EPSILON = 0.03
ALPHA = 0.005
PGD_STEPS = 10

EPOCHS = 1
BATCH_SIZE = 64
LEARNING_RATE = 0.0001

MODEL_PATH = "model/weights/defended_model.pth"
OUTPUT_PATH = "model/weights/pgd_defended_model.pth"


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
# Load training data
# -----------------------------------

train_dataset = datasets.CIFAR10(
    root="./data",
    train=True,
    download=True,
    transform=transform
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)


# -----------------------------------
# Load FGSM-defended model
# -----------------------------------

model = SimpleCNN()

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location="cpu"
    )
)

model.train()


# -----------------------------------
# Optimizer and loss
# -----------------------------------

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)

criterion = torch.nn.CrossEntropyLoss()


# -----------------------------------
# PGD Attack
# -----------------------------------

def pgd_attack(model, images, labels):

    original_images = images.detach().clone()

    # Start from the original image
    adversarial_images = images.detach().clone()

    for _ in range(PGD_STEPS):

        adversarial_images.requires_grad = True

        outputs = model(adversarial_images)

        loss = criterion(outputs, labels)

        model.zero_grad()

        loss.backward()

        gradient = adversarial_images.grad.data

        # PGD update
        adversarial_images = (
            adversarial_images.detach()
            + ALPHA * gradient.sign()
        )

        # Keep perturbation within epsilon
        perturbation = (
            adversarial_images - original_images
        )

        perturbation = torch.clamp(
            perturbation,
            -EPSILON,
            EPSILON
        )

        adversarial_images = (
            original_images + perturbation
        )

        # Keep normalized values in a reasonable range
        adversarial_images = torch.clamp(
            adversarial_images,
            -3,
            3
        )

    return adversarial_images.detach()


# -----------------------------------
# PGD Adversarial Training
# -----------------------------------

print("----- PGD Adversarial Training -----")

for epoch in range(EPOCHS):

    total_loss = 0

    for images, labels in train_loader:

        # Generate PGD adversarial examples
        adversarial_images = pgd_attack(
            model,
            images,
            labels
        )

        # Train on PGD examples
        optimizer.zero_grad()

        adversarial_outputs = model(
            adversarial_images
        )

        adversarial_loss = criterion(
            adversarial_outputs,
            labels
        )

        adversarial_loss.backward()

        optimizer.step()

        total_loss += adversarial_loss.item()

    average_loss = (
        total_loss / len(train_loader)
    )

    print(
        f"Epoch {epoch + 1}/{EPOCHS} "
        f"- Loss: {average_loss:.4f}"
    )


# -----------------------------------
# Save PGD-defended model
# -----------------------------------

torch.save(
    model.state_dict(),
    OUTPUT_PATH
)

print("\n----- PGD Defense Complete -----")
print(f"Saved defended model: {OUTPUT_PATH}")