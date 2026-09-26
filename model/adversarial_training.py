import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from model import SimpleCNN


# -----------------------------------
# Configuration
# -----------------------------------

EPSILON = 0.03
EPOCHS = 1
BATCH_SIZE = 64
LEARNING_RATE = 0.0001

MODEL_PATH = "model/weights/pytorch_model.bin"
OUTPUT_PATH = "model/weights/defended_model.pth"


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
# Load pretrained model
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
# Adversarial training
# -----------------------------------

print("----- Adversarial Training -----")

for epoch in range(EPOCHS):

    total_loss = 0

    for images, labels in train_loader:

        images.requires_grad = True

        # Clean prediction
        outputs = model(images)

        clean_loss = criterion(
            outputs,
            labels
        )

        # Generate FGSM examples
        model.zero_grad()

        clean_loss.backward(
            retain_graph=True
        )

        gradient = images.grad.data

        adversarial_images = (
            images
            + EPSILON * gradient.sign()
        )

        adversarial_images = torch.clamp(
            adversarial_images,
            -3,
            3
        )

        # Train on adversarial examples
        optimizer.zero_grad()

        adversarial_outputs = model(
            adversarial_images.detach()
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
# Save defended model
# -----------------------------------

torch.save(
    model.state_dict(),
    OUTPUT_PATH
)

print("\n----- Defense Complete -----")
print(f"Saved defended model: {OUTPUT_PATH}")

