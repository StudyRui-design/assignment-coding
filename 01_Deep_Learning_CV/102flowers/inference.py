# -*- coding: utf-8 -*-
"""
Inference module — loads the trained ResNet18 model and provides
single-image prediction for the 102-flowers classification task.

Preprocessing is kept identical to predict.py / test.py.
"""

import os
import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import numpy as np
from typing import Tuple, List, Dict, Optional

from config import Config
from flower_names import FLOWER_NAMES


# ---------------------------------------------------------------------------
# Global cache — load model once, reuse across requests
# ---------------------------------------------------------------------------
_model = None
_device = None
_transform = None
_class_names: list = []          # e.g. ["001", "002", …, "102"]


def _build_transform() -> transforms.Compose:
    """Build the inference transform — MUST match predict.py exactly."""
    cfg = Config()
    return transforms.Compose([
        transforms.Resize((cfg.image_size, cfg.image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=cfg.norm_mean, std=cfg.norm_std),
    ])


def load_model() -> Tuple[torch.nn.Module, torch.device, transforms.Compose, list]:
    """
    Load the trained ResNet18 model from the full checkpoint.

    Returns
    -------
    model : torch.nn.Module
        ResNet18 in eval mode, on the correct device.
    device : torch.device
    transform : torchvision.transforms.Compose
    class_names : list[str]
        Folder-style class names ("001"-"102").
    """
    global _model, _device, _transform, _class_names

    if _model is not None:
        return _model, _device, _transform, _class_names

    cfg = Config()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # --- locate checkpoint ---------------------------------------------------
    checkpoint_path = cfg.model_save_path
    if not os.path.exists(checkpoint_path):
        # fallback: try project models/ directory
        alt = os.path.join(os.path.dirname(__file__), "models", "best_model.pth")
        if os.path.exists(alt):
            checkpoint_path = alt
        else:
            raise FileNotFoundError(
                f"Checkpoint not found at {cfg.model_save_path} or {alt}"
            )

    # --- load checkpoint -----------------------------------------------------
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    # class names
    class_names = checkpoint.get("class_names", [])
    if not class_names:
        # If checkpoint only has weights, derive from dataset folder order
        import torchvision.datasets as ds
        if os.path.exists(cfg.test_dir):
            tmp = ds.ImageFolder(cfg.test_dir)
            class_names = tmp.classes
    if len(class_names) != 102:
        raise RuntimeError(
            f"Expected 102 class names, got {len(class_names)}. "
            f"Check the checkpoint file at {checkpoint_path}"
        )

    # --- build model ---------------------------------------------------------
    model = models.resnet18()
    model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device).eval()

    # --- transform -----------------------------------------------------------
    transform = _build_transform()

    # cache
    _model, _device, _transform, _class_names = model, device, transform, class_names
    return _model, _device, _transform, _class_names


def predict_single(
    image: Image.Image,
    return_top_k: int = 5,
) -> Dict:
    """
    Run inference on a single PIL Image.

    Parameters
    ----------
    image : PIL.Image.Image
        Input image (RGB).
    return_top_k : int
        Number of top predictions to return (default 5).

    Returns
    -------
    dict with keys:
        predicted_idx    : int            — predicted class index (0-101)
        predicted_name   : str            — English flower name
        confidence       : float          — confidence of top-1 (0-1)
        top_k_indices    : list[int]      — top-K class indices
        top_k_names      : list[str]      — top-K flower names
        top_k_probs      : list[float]    — top-K confidence scores
        all_probs        : np.ndarray     — full 102-dim probability vector
    """
    model, device, transform, class_names = load_model()

    # preprocess
    img_tensor = transform(image).unsqueeze(0).to(device)

    # inference
    with torch.no_grad():
        output = model(img_tensor)
        probs = F.softmax(output, dim=1).cpu().numpy().flatten()

    # top-1
    top1_idx = int(np.argmax(probs))
    top1_conf = float(probs[top1_idx])

    # top-K
    top_k_indices = np.argsort(probs)[::-1][:return_top_k].tolist()
    top_k_probs = [float(probs[i]) for i in top_k_indices]
    top_k_names = [FLOWER_NAMES[i] for i in top_k_indices]

    return {
        "predicted_idx": top1_idx,
        "predicted_name": FLOWER_NAMES[top1_idx],
        "confidence": top1_conf,
        "top_k_indices": top_k_indices,
        "top_k_names": top_k_names,
        "top_k_probs": top_k_probs,
        "all_probs": probs,
    }


def get_all_class_names() -> list:
    """Return the list of 102 English flower names (index 0-101)."""
    return FLOWER_NAMES


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Loading model …")
    model, device, transform, class_names = load_model()
    print(f"  Device: {device}")
    print(f"  Classes: {len(class_names)}")
    print(f"  First 3 class folders: {class_names[:3]}")
    print("  ✓ Model ready.")
