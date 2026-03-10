from pathlib import Path
from typing import Any, Tuple, Dict

import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
import numpy as np


MODEL_DIR = Path(__file__).parent.parent / "model"
# Prefer your ResNet18 model; fallback to any .pt in model/
MODEL_PATH = MODEL_DIR / "best_model_resnet18_cn_mci_ad.pt"
if not MODEL_PATH.exists():
    MODEL_PATH = next((f for f in MODEL_DIR.glob("*.pt")), None)

# Matches training: 0=AD, 1=CN, 2=MCI
CLASS_NAMES = ["Alzheimer's Disease", "Cognitively Normal", "Mild Cognitive Impairment (MCI)"]

_model: Any = None


def _build_resnet18_3class():
    """ResNet18 with 3-class output for CN / MCI / AD."""
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))
    return model


def load_model():
    global _model
    if _model is not None:
        return _model
    if MODEL_PATH is None or not MODEL_PATH.exists():
        return None
    obj = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    # State_dict only: load into ResNet18 with 3 classes
    if isinstance(obj, dict):
        model = _build_resnet18_3class()
        model.load_state_dict(obj, strict=False)
        _model = model
    else:
        _model = obj
    if hasattr(_model, "eval"):
        _model.eval()
    return _model


def _preprocess_image(file_path: Path) -> torch.Tensor:
    """Load image, resize to 224x224, normalize for typical ImageNet-style models."""
    img = Image.open(file_path).convert("RGB")
    img = img.resize((224, 224), Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    # Normalize if model expects ImageNet stats (optional; many .pt models do)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    arr = (arr - mean) / std
    tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)  # (1, 3, 224, 224)
    return tensor


def run_inference(file_path: Path) -> Tuple[str, float, Dict[str, float]]:
    """Returns (label, confidence, probs_dict) where probs_dict has class name -> probability."""
    model = load_model()
    if model is None:
        return "Model not loaded (add a .pt file to the model/ folder)", 0.0, {}

    try:
        x = _preprocess_image(file_path)
    except Exception as e:
        return f"Invalid image: {e}", 0.0, {}

    # Match input dtype to model (model may be float64 if trained with double precision)
    model_dtype = next(model.parameters()).dtype
    x = x.to(model_dtype)

    with torch.no_grad():
        out = model(x)

    # Handle tuple output (e.g. (logits,)) or single tensor
    if isinstance(out, (list, tuple)):
        out = out[0]
    logits = out if isinstance(out, torch.Tensor) else torch.tensor(out)
    if logits.dim() == 1:
        logits = logits.unsqueeze(0)
    probs = torch.softmax(logits, dim=-1)[0]
    prob_np = probs.cpu().numpy()

    idx = int(torch.argmax(probs).item())
    confidence = float(prob_np[idx])
    labels = CLASS_NAMES if len(CLASS_NAMES) >= len(prob_np) else [f"Class {i}" for i in range(len(prob_np))]
    label = labels[idx] if idx < len(labels) else f"Class {idx}"

    probs_dict = {labels[i]: float(prob_np[i]) for i in range(min(len(labels), len(prob_np)))}
    return label, confidence, probs_dict
