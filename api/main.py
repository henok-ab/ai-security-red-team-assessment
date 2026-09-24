import io

import torch
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from torchvision import transforms

from model.model import SimpleCNN


# -----------------------------
# 1. Create FastAPI application
# -----------------------------

app = FastAPI(
    title="CIFAR-10 AI Model API",
    version="1.0"
)


# -----------------------------
# 2. Load model
# -----------------------------

MODEL_PATH = "model/weights/pytorch_model.bin"

model = SimpleCNN()

state_dict = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

model.load_state_dict(state_dict)
model.eval()


# -----------------------------
# 3. Class names
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
# 4. Preprocessing
# -----------------------------

transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2023, 0.1994, 0.2010)
    )
])


# -----------------------------
# 5. Health endpoint
# -----------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -----------------------------
# 6. Prediction endpoint
# -----------------------------

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # Read uploaded image
    image_bytes = await file.read()

    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    # Preprocess
    image_tensor = transform(image)

    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)

    # Model prediction
    with torch.no_grad():

        outputs = model(image_tensor)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        predicted_label = torch.argmax(
            probabilities,
            dim=1
        ).item()

        confidence = probabilities[
            0,
            predicted_label
        ].item()

    return {
        "predicted_class": classes[predicted_label],
        "confidence": round(confidence, 4)
    }