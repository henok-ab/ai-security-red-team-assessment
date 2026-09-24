import torch
from torchvision import datasets, transforms
from model import SimpleCNN

MODEL_PATH = "model/weights/pytorch_model.bin"

EPSILONS = [0.00, 0.01, 0.03, 0.05, 0.10]

model = SimpleCNN()

state_dict = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

model.load_state_dict(state_dict)
model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2023, 0.1994, 0.2010)
    )
])

dataset = datasets.CIFAR10(
    root="data",
    train=False,
    download=True,
    transform=transform
)

total = len(dataset)

print("----- FGSM Robustness Evaluation -----")
print(f"Test images: {total}")
print()

for epsilon in EPSILONS:

    correct = 0
    attack_successes = 0
    eligible_images = 0

    for image, label in dataset:

        image = image.unsqueeze(0)
        label_tensor = torch.tensor([label])

        # Clean prediction
        image.requires_grad = True

        output = model(image)

        clean_prediction = torch.argmax(
            output,
            dim=1
        ).item()

        # We only measure attack success
        # on images correctly classified originally
        if clean_prediction != label:
            continue

        eligible_images += 1

        # No attack for epsilon = 0
        if epsilon == 0.0:

            correct += 1
            continue

        loss = torch.nn.functional.cross_entropy(
            output,
            label_tensor
        )

        model.zero_grad()
        loss.backward()

        perturbation = epsilon * image.grad.sign()

        adversarial_image = image + perturbation

        with torch.no_grad():

            adversarial_output = model(
                adversarial_image
            )

            adversarial_prediction = torch.argmax(
                adversarial_output,
                dim=1
            ).item()

        if adversarial_prediction == label:
            correct += 1
        else:
            attack_successes += 1

    adversarial_accuracy = (
        correct / eligible_images * 100
        if eligible_images > 0
        else 0
    )

    attack_success_rate = (
        attack_successes / eligible_images * 100
        if eligible_images > 0
        else 0
    )

    print(
        f"Epsilon: {epsilon:.2f} | "
        f"Accuracy: {adversarial_accuracy:.2f}% | "
        f"Attack Success: {attack_success_rate:.2f}%"
    )