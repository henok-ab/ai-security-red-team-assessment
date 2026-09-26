import torch
from torchvision import datasets, transforms
from model import SimpleCNN


# -----------------------------------
# Configuration
# -----------------------------------

EPSILON = 0.03

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
# Dataset
# -----------------------------------

test_dataset = datasets.CIFAR10(
    root="./data",
    train=False,
    download=True,
    transform=transform
)


# -----------------------------------
# Load models
# -----------------------------------

original_model = SimpleCNN()

original_model.load_state_dict(
    torch.load(
        ORIGINAL_MODEL,
        map_location="cpu"
    )
)

original_model.eval()


defended_model = SimpleCNN()

defended_model.load_state_dict(
    torch.load(
        DEFENDED_MODEL,
        map_location="cpu"
    )
)

defended_model.eval()


# -----------------------------------
# FGSM evaluation
# -----------------------------------

def evaluate_model(model, model_name):

    correct_clean = 0
    successful_attacks = 0
    evaluated = 0

    for image, label in test_dataset:

        image = image.unsqueeze(0)
        label_tensor = torch.tensor([label])

        # Clean prediction
        image.requires_grad = True

        output = model(image)

        clean_prediction = output.argmax(
            dim=1
        ).item()

        # Only evaluate initially
        # correctly classified images
        if clean_prediction != label:
            continue

        correct_clean += 1

        # Calculate gradient
        loss = torch.nn.functional.cross_entropy(
            output,
            label_tensor
        )

        model.zero_grad()

        loss.backward()

        gradient = image.grad.data

        # FGSM
        adversarial_image = (
            image
            + EPSILON * gradient.sign()
        )

        adversarial_image = torch.clamp(
            adversarial_image,
            -3,
            3
        )

        # Adversarial prediction
        with torch.no_grad():

            adversarial_output = model(
                adversarial_image
            )

            adversarial_prediction = (
                adversarial_output.argmax(
                    dim=1
                ).item()
            )

        evaluated += 1

        if adversarial_prediction != label:
            successful_attacks += 1

    attack_success_rate = (
        successful_attacks / evaluated
    ) * 100

    print(f"\n----- {model_name} -----")
    print(f"Initially correct: {correct_clean}")
    print(f"Successful attacks: {successful_attacks}")
    print(f"Attack Success Rate: {attack_success_rate:.2f}%")


# -----------------------------------
# Run comparison
# -----------------------------------

print("===== FGSM DEFENSE COMPARISON =====")
print(f"Epsilon: {EPSILON}")

evaluate_model(
    original_model,
    "Original Model"
)

evaluate_model(
    defended_model,
    "Defended Model"
)

