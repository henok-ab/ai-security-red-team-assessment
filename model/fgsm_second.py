import torch
from torchvision import datasets, transforms
from PIL import Image
from model import SimpleCNN

# -----------------------------
# Configuration
# -----------------------------
EPSILON = 0.03
IMAGE_INDEX = 4

# CIFAR-10 class names
classes = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
]

# -----------------------------
# Load model
# -----------------------------
model = SimpleCNN()
model.load_state_dict(
    torch.load(
        "model/weights/pytorch_model.bin",
        map_location="cpu"
    )
)
model.eval()

# -----------------------------
# Load CIFAR-10 test image
# -----------------------------
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2470, 0.2435, 0.2616)
    )
])

dataset = datasets.CIFAR10(
    root="./data",
    train=False,
    download=True,
    transform=transform
)

image, label = dataset[IMAGE_INDEX]
image = image.unsqueeze(0)
image.requires_grad = True

# -----------------------------
# Clean prediction
# -----------------------------
output = model(image)
clean_prediction = output.argmax(dim=1).item()

# -----------------------------
# FGSM attack
# -----------------------------
loss = torch.nn.functional.cross_entropy(
    output,
    torch.tensor([label])
)

model.zero_grad()
loss.backward()

gradient = image.grad.data

adversarial_image = image + EPSILON * gradient.sign()
adversarial_image = torch.clamp(adversarial_image, -3, 3)

# -----------------------------
# Adversarial prediction
# -----------------------------
adv_output = model(adversarial_image)
adv_prediction = adv_output.argmax(dim=1).item()

print("----- FGSM Second Attack -----")
print(f"Image index: {IMAGE_INDEX}")
print(f"True label: {classes[label]}")
print(f"Clean prediction: {classes[clean_prediction]}")
print(f"Adversarial prediction: {classes[adv_prediction]}")
print(f"Epsilon: {EPSILON}")
print(
    f"Attack successful: "
    f"{clean_prediction != adv_prediction}"
)

# -----------------------------
# Save images
# -----------------------------
def save_image(tensor, filename):
    image = tensor.squeeze(0).detach().cpu()

    mean = torch.tensor([0.4914, 0.4822, 0.4465]).view(3, 1, 1)
    std = torch.tensor([0.2470, 0.2435, 0.2616]).view(3, 1, 1)

    image = image * std + mean
    image = torch.clamp(image, 0, 1)

    image = transforms.ToPILImage()(image)
    image.save(filename)


save_image(
    image,
    "results/adversarial/clean_frog.png"
)

save_image(
    adversarial_image,
    "results/adversarial/fgsm_frog_to_deer.png"
)

print("\n----- Saved Images -----")
print("Clean image: results/adversarial/clean_frog.png")
print("Adversarial image: results/adversarial/fgsm_frog_to_deer.png")