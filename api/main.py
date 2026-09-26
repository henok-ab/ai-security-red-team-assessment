import io

import torch
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, File, HTTPException, UploadFile
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
# 2. Security limits
# -----------------------------

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_WIDTH = 1024
MAX_IMAGE_HEIGHT = 1024


# -----------------------------
# 3. Load model
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
# 4. Class names
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
# 5. Preprocessing
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
# 6. Health endpoint
# -----------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -----------------------------
# 7. Prediction endpoint
# -----------------------------

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # Read uploaded file
    image_bytes = await file.read()

    # Check file size
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 5 MB."
        )

    # Check that the uploaded content is a valid image
    try:
        image_file = Image.open(
            io.BytesIO(image_bytes)
        )

        # Verify image integrity
        image_file.verify()

        # Re-open because verify() consumes the image object
        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file."
        )

    # Check image dimensions
    width, height = image.size

    if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
        raise HTTPException(
            status_code=413,
            detail="Image dimensions are too large."
        )

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

