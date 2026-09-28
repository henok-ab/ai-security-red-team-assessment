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

BATCH_SIZE = 64

MODELS = {
    "Original": "model/weights/pytorch_model.bin",
    "FGSM Defense": "model/weights/defended_model.pth",
    "PGD Defense": "model/weights/pgd_defended_model.pth",
}


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
# Load test dataset
# -----------------------------------

test_dataset = datasets.CIFAR10(
    root="./data",
    train=False,
    download=True,
    transform=transform
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# -----------------------------------
# PGD attack
# -----------------------------------

def pgd_attack(model, images, labels):

    original_images = images.detach().clone()

    # Start from clean images
    adversarial_images = images.detach().clone()

    for _ in range(PGD_STEPS):

        adversarial_images.requires_grad = True

        outputs = model(adversarial_images)

        loss = torch.nn.functional.cross_entropy(
            outputs,
            labels
        )

        model.zero_grad()

        loss.backward()

        gradient = adversarial_images.grad.data

        # PGD update
        adversarial_images = (
            adversarial_images.detach()
            + ALPHA * gradient.sign()
        )

        # Keep perturbation inside epsilon
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

        # Keep normalized values reasonable
        adversarial_images = torch.clamp(
            adversarial_images,
            -3,
            3
        )

    return adversarial_images.detach()


# -----------------------------------
# Evaluate one model
# -----------------------------------

def evaluate_model(model_path):

    model = SimpleCNN()

    model.load_state_dict(
        torch.load(
            model_path,
            map_location="cpu"
        )
    )

    model.eval()

    total_clean_correct = 0
    total_attacked = 0
    total_successful_attacks = 0

    for images, labels in test_loader:

        # -----------------------------------
        # Clean predictions
        # -----------------------------------

        with torch.no_grad():

            outputs = model(images)

            clean_predictions = outputs.argmax(
                dim=1
            )

        # Only attack images the model
        # classified correctly
        correct_mask = (
            clean_predictions == labels
        )

        if correct_mask.sum() == 0:
            continue

        clean_images = images[correct_mask]
        clean_labels = labels[correct_mask]

        total_clean_correct += clean_labels.size(0)

        # -----------------------------------
        # Generate PGD examples
        # -----------------------------------

        adversarial_images = pgd_attack(
            model,
            clean_images,
            clean_labels
        )

        # -----------------------------------
        # Adversarial predictions
        # -----------------------------------

        with torch.no_grad():

            adversarial_outputs = model(
                adversarial_images
            )

            adversarial_predictions = (
                adversarial_outputs.argmax(dim=1)
            )

        # Count successful attacks
        successful_attacks = (
            adversarial_predictions != clean_labels
        ).sum().item()

        total_successful_attacks += successful_attacks
        total_attacked += clean_labels.size(0)

    # -----------------------------------
    # Calculate results
    # -----------------------------------

    attack_success_rate = (
        total_successful_attacks /
        total_attacked
    ) * 100

    remaining_accuracy = (
        (total_attacked - total_successful_attacks) /
        total_attacked
    ) * 100

    return (
        total_attacked,
        attack_success_rate,
        remaining_accuracy
    )


# -----------------------------------
# Run comparison
# -----------------------------------

print("\n======================================")
print("       PGD DEFENSE COMPARISON")
print("======================================")

print(f"Epsilon: {EPSILON}")
print(f"Alpha: {ALPHA}")
print(f"PGD Steps: {PGD_STEPS}")

results = {}

for name, path in MODELS.items():

    print(f"\nTesting: {name}")

    attacked, asr, accuracy = evaluate_model(path)

    results[name] = (attacked, asr, accuracy)

    print(f"Correctly classified and attacked: {attacked}")
    print(f"PGD Attack Success Rate: {asr:.2f}%")
    print(f"Accuracy after PGD attack: {accuracy:.2f}%")


# -----------------------------------
# Final comparison
# -----------------------------------

print("\n======================================")
print("             FINAL RESULTS")
print("======================================")

print(
    f"{'Model':<20}"
    f"{'PGD ASR':>12}"
    f"{'Remaining Acc.':>18}"
)

print("-" * 50)

for name, (_, asr, accuracy) in results.items():

    print(
        f"{name:<20}"
        f"{asr:>11.2f}%"
        f"{accuracy:>17.2f}%"
    )

print("======================================")

