import torch
from torchvision import datasets, transforms
from model import SimpleCNN
from PIL import Image
from pathlib import Path

MODEL_PATH = "model/weights/pytorch_model.bin"
EPSILON = 0.03
IMAGE_INDEX = 0

# CIFAR-10 normalization values
MEAN = torch.tensor([0.4914, 0.4822, 0.4465]).view(1, 3, 1, 1)
STD = torch.tensor([0.2023, 0.1994, 0.2010]).view(1, 3, 1, 1)

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

image, label = dataset[IMAGE_INDEX]

image = image.unsqueeze(0)
label = torch.tensor([label])

image.requires_grad = True

# -----------------------------
# Generate adversarial example
# -----------------------------

output = model(image)

loss = torch.nn.functional.cross_entropy(
    output,
    label
)

model.zero_grad()
loss.backward()

perturbation = EPSILON * image.grad.sign()

adversarial_image = image + perturbation

# -----------------------------
# Predictions
# -----------------------------

with torch.no_grad():

    clean_output = model(image)
    adversarial_output = model(adversarial_image)

    clean_prediction = torch.argmax(
        clean_output,
        dim=1
    ).item()

    adversarial_prediction = torch.argmax(
        adversarial_output,
        dim=1
    ).item()

# -----------------------------
# CIFAR-10 class names
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
# Save images
# -----------------------------

output_dir = Path("results/adversarial")
output_dir.mkdir(
    parents=True,
    exist_ok=True
)

# Undo normalization
clean_image = image.detach() * STD + MEAN
adv_image = adversarial_image.detach() * STD + MEAN

# Keep pixel values between 0 and 1
clean_image = clean_image.clamp(0, 1)
adv_image = adv_image.clamp(0, 1)

# Convert tensor → PIL image
clean_pil = transforms.ToPILImage()(
    clean_image.squeeze(0)
)

adv_pil = transforms.ToPILImage()(
    adv_image.squeeze(0)
)

clean_path = output_dir / "clean_cat.png"
adv_path = output_dir / "fgsm_cat_to_frog.png"

clean_pil.save(clean_path)
adv_pil.save(adv_path)

# -----------------------------
# Results
# -----------------------------

print("----- FGSM Attack -----")
print(f"True label: {classes[label.item()]}")
print(f"Clean prediction: {classes[clean_prediction]}")
print(f"Adversarial prediction: {classes[adversarial_prediction]}")
print(f"Epsilon: {EPSILON}")
print(f"Attack successful: {clean_prediction != adversarial_prediction}")

print()
print("----- Saved Images -----")
print(f"Clean image: {clean_path}")
print(f"Adversarial image: {adv_path}")