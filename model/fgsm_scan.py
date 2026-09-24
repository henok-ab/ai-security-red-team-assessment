import torch
from torchvision import datasets, transforms
from model import SimpleCNN

MODEL_PATH = "model/weights/pytorch_model.bin"
EPSILON = 0.03

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

successful = 0

for index in range(100):

    image, label = dataset[index]

    image = image.unsqueeze(0)
    label_tensor = torch.tensor([label])

    image.requires_grad = True

    output = model(image)

    clean_prediction = torch.argmax(
        output,
        dim=1
    ).item()

    # Only attack images the model gets correct
    if clean_prediction != label:
        continue

    loss = torch.nn.functional.cross_entropy(
        output,
        label_tensor
    )

    model.zero_grad()
    loss.backward()

    perturbation = EPSILON * image.grad.sign()

    adversarial_image = image + perturbation

    with torch.no_grad():

        adversarial_output = model(
            adversarial_image
        )

        adversarial_prediction = torch.argmax(
            adversarial_output,
            dim=1
        ).item()

    if adversarial_prediction != clean_prediction:

        print("----- Successful Attack -----")
        print(f"Image index: {index}")
        print(f"True label: {classes[label]}")
        print(f"Clean prediction: {classes[clean_prediction]}")
        print(
            f"Adversarial prediction: "
            f"{classes[adversarial_prediction]}"
        )
        print(f"Epsilon: {EPSILON}")

        successful += 1

        if successful == 5:
            break

print()
print(f"Successful attacks found: {successful}")