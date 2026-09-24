from huggingface_hub import hf_hub_download
from pathlib import Path

MODEL_REPO = "manasyesuarthana/cifar10-simple-cnn-pytorch"
MODEL_FILE = "pytorch_model.bin"

output_dir = Path(__file__).parent / "weights"
output_dir.mkdir(parents=True, exist_ok=True)

model_path = hf_hub_download(
    repo_id=MODEL_REPO,
    filename=MODEL_FILE,
    local_dir=output_dir
)

print(f"Model downloaded to: {model_path}")
