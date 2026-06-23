# -*- coding: utf-8 -*-
"""
Evaluation & chart generation.
Runs the trained ResNet18 model on the test set to produce:
  - confusion_matrix.json   : 102x102 raw matrix + class lists
  - per_class_metrics.json  : recall, precision per class
  - evaluation_summary.json : top-level accuracies + recall distribution
  - predictions.json        : per-image (path, true, pred, confidence)
  - top_confusions.json     : top-10 most-confused flower pairs
"""

import os
import json
import time
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sklearn.metrics import (
    confusion_matrix,
    precision_recall_fscore_support,
    classification_report,
)

from config import Config
from inference import load_model
from flower_names import FLOWER_NAMES

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
EVAL_DIR = os.path.join(os.path.dirname(__file__), "evaluation_data")
os.makedirs(EVAL_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Run full test-set evaluation
# ---------------------------------------------------------------------------
def run_evaluation(save: bool = True) -> dict:
    """
    Evaluate the model on the entire test set.

    Returns a dict with keys:
      cm          : np.ndarray (102,102)
      recall      : np.ndarray (102,)
      precision   : np.ndarray (102,)
      f1          : np.ndarray (102,)
      accuracy    : float
      all_labels  : list[int]
      all_preds   : list[int]
      class_names : list[str]  — folder names "001"-"102"
      predictions : list[dict] — per-image prediction records
    """
    cfg = Config()
    model, device, _, _ = load_model()
    class_names = [f"{i:03d}" for i in range(1, 103)]  # folder-style

    # transform — same as test.py / predict.py
    eval_transform = transforms.Compose([
        transforms.Resize((cfg.image_size, cfg.image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=cfg.norm_mean, std=cfg.norm_std),
    ])

    print(f"Loading test dataset from {cfg.test_dir} …")
    test_dataset = datasets.ImageFolder(cfg.test_dir, transform=eval_transform)
    test_loader = DataLoader(test_dataset, batch_size=cfg.batch_size, shuffle=False,
                             num_workers=cfg.num_workers)

    print(f"  Test samples: {len(test_dataset)}")
    print(f"  Classes: {len(test_dataset.classes)}")

    # Build image-path list (same order as DataLoader with shuffle=False)
    image_paths = [os.path.relpath(p, cfg.test_dir).replace("\\", "/")
                   for p, _ in test_dataset.samples]

    all_preds, all_labels, all_confs = [], [], []
    t0 = time.time()
    with torch.no_grad():
        for imgs, labels in test_loader:
            imgs = imgs.to(device)
            outputs = model(imgs)
            probs = F.softmax(outputs, dim=1)
            confs, preds = torch.max(probs, 1)
            all_preds.extend(preds.cpu().numpy().tolist())
            all_labels.extend(labels.numpy().tolist())
            all_confs.extend(confs.cpu().numpy().tolist())
    elapsed = time.time() - t0
    print(f"  Inference done in {elapsed:.1f}s ({len(test_dataset)/elapsed:.0f} img/s)")

    # --- Build per-image predictions ------------------------------------------
    predictions = []
    for i in range(len(image_paths)):
        predictions.append({
            "path": image_paths[i],
            "true_label": int(all_labels[i]),
            "true_name": FLOWER_NAMES[all_labels[i]],
            "pred_label": int(all_preds[i]),
            "pred_name": FLOWER_NAMES[all_preds[i]],
            "confidence": round(float(all_confs[i]), 4),
            "correct": bool(all_labels[i] == all_preds[i]),
        })

    # --- Metrics ---------------------------------------------------------------
    cm = confusion_matrix(all_labels, all_preds)  # shape (102, 102)
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, labels=list(range(102)), zero_division=0
    )
    accuracy = 100.0 * sum(a == b for a, b in zip(all_labels, all_preds)) / len(all_labels)

    print(f"  Accuracy: {accuracy:.2f}%")

    # --- Top confusion pairs (off-diagonal) ------------------------------------
    top_confusions = _compute_top_confusions(cm)
    print(f"  Top confusion pairs computed: {len(top_confusions)}")

    result = {
        "cm": cm,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "accuracy": accuracy,
        "all_labels": all_labels,
        "all_preds": all_preds,
        "class_names": class_names,
        "predictions": predictions,
        "top_confusions": top_confusions,
    }

    if save:
        _save_evaluation_data(result)

    return result


def _compute_top_confusions(cm: np.ndarray, top_k: int = 10) -> list:
    """
    Find the top-K most-confused pairs (true≠pred) from the confusion matrix.

    Returns list of dicts sorted by count descending:
      {true_label, true_name, pred_label, pred_name, count}
    """
    pairs = []
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            if i != j and cm[i, j] > 0:
                pairs.append({
                    "true_label": int(i),
                    "true_name": FLOWER_NAMES[i],
                    "pred_label": int(j),
                    "pred_name": FLOWER_NAMES[j],
                    "count": int(cm[i, j]),
                })
    pairs.sort(key=lambda x: x["count"], reverse=True)
    return pairs[:top_k]


def _save_evaluation_data(data: dict):
    """Persist all evaluation results as JSON files."""
    cm = data["cm"]
    predictions = data["predictions"]
    recall = data["recall"]
    precision = data["precision"]
    f1 = data["f1"]
    n_correct = sum(1 for p in predictions if p["correct"])
    n_total = len(predictions)
    n_incorrect = n_total - n_correct

    # --- confusion_matrix.json ------------------------------------------------
    with open(os.path.join(EVAL_DIR, "confusion_matrix.json"), "w", encoding="utf-8") as f:
        json.dump({
            "matrix": cm.tolist(),
            "class_names": data["class_names"],
            "flower_names": FLOWER_NAMES,
        }, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved confusion_matrix.json ({cm.shape})")

    # --- per_class_metrics.json -----------------------------------------------
    per_class = []
    recall_100 = []
    lowest_recall = {"name": "", "folder": "", "recall": 1.0}
    for i in range(102):
        r = round(float(recall[i]), 4)
        p = round(float(precision[i]), 4)
        f = round(float(f1[i]), 4)
        per_class.append({
            "index": i,
            "folder": f"{i+1:03d}",
            "name": FLOWER_NAMES[i],
            "recall": r,
            "precision": p,
            "f1": f,
        })
        if r >= 1.0:
            recall_100.append(FLOWER_NAMES[i])
        if r < lowest_recall["recall"]:
            lowest_recall = {"name": FLOWER_NAMES[i], "folder": f"{i+1:03d}", "recall": r}

    with open(os.path.join(EVAL_DIR, "per_class_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(per_class, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved per_class_metrics.json")

    # --- evaluation_summary.json (expanded) -----------------------------------
    recall_values = [recall[i] for i in range(102)]
    ge90 = sum(1 for r in recall_values if r >= 0.9)
    ge50 = sum(1 for r in recall_values if r >= 0.5)
    lt30 = sum(1 for r in recall_values if r < 0.3)

    with open(os.path.join(EVAL_DIR, "evaluation_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": round(data["accuracy"], 2),
            "num_classes": 102,
            "num_samples": n_total,
            "correct": n_correct,
            "incorrect": n_incorrect,
            "avg_recall": round(float(np.mean(recall)) * 100, 2),
            "avg_precision": round(float(np.mean(precision)) * 100, 2),
            "avg_f1": round(float(np.mean(f1)) * 100, 2),
            "recall_ge90_count": ge90,
            "recall_ge90_pct": round(ge90 / 102 * 100, 1),
            "recall_ge50_count": ge50,
            "recall_ge50_pct": round(ge50 / 102 * 100, 1),
            "recall_lt30_count": lt30,
            "recall_lt30_pct": round(lt30 / 102 * 100, 1),
            "recall_100_classes": recall_100,
            "recall_lowest": lowest_recall,
        }, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved evaluation_summary.json")

    # --- predictions.json — per-image records ----------------------------------
    with open(os.path.join(EVAL_DIR, "predictions.json"), "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved predictions.json ({len(predictions)} records)")

    # --- top_confusions.json — with example images -----------------------------
    # Enrich each pair with actual image paths from predictions
    enriched = []
    for pair in data["top_confusions"]:
        # Find first matching misclassified image (true side)
        example = next(
            (p for p in predictions
             if p["true_label"] == pair["true_label"]
             and p["pred_label"] == pair["pred_label"]
             and not p["correct"]),
            None
        )
        pair["example_true_path"] = example["path"] if example else ""
        # For "pred" side, find any correctly-classified image from that class
        pred_example = next(
            (p for p in predictions
             if p["true_label"] == pair["pred_label"]
             and p["correct"]),
            None
        )
        pair["example_pred_path"] = pred_example["path"] if pred_example else ""
        enriched.append(pair)

    with open(os.path.join(EVAL_DIR, "top_confusions.json"), "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved top_confusions.json ({len(enriched)} pairs)")


# ---------------------------------------------------------------------------
# 2. Plotly chart builders (called from Flask routes)
# ---------------------------------------------------------------------------
def build_confusion_matrix_heatmap():
    """
    Returns a Plotly Figure for the 102x102 confusion matrix.
    Interactive: hover shows exact value, no text labels on cells (readability).
    """
    import plotly.graph_objects as go

    json_path = os.path.join(EVAL_DIR, "confusion_matrix.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cm = np.array(data["matrix"])
    names = [f"{i+1:03d} {FLOWER_NAMES[i]}" for i in range(102)]

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=names,
        y=names,
        colorscale="Blues",
        hovertemplate=(
            "True: %{y}<br>"
            "Pred: %{x}<br>"
            "Count: %{z}<extra></extra>"
        ),
        colorbar=dict(title="Count"),
    ))

    fig.update_layout(
        title="Confusion Matrix (102 Classes) — Hover to see values",
        xaxis_title="Predicted",
        yaxis_title="True",
        width=1200,
        height=1100,
        xaxis=dict(tickfont=dict(size=6), tickangle=90),
        yaxis=dict(tickfont=dict(size=6)),
    )

    return fig


def build_recall_chart(sort_by: str = "recall"):
    """
    Build a Plotly bar chart of per-class recall.

    Parameters
    ----------
    sort_by : str
        "recall" → sort by recall descending;
        "index" → keep class order.
    """
    import plotly.graph_objects as go

    json_path = os.path.join(EVAL_DIR, "per_class_metrics.json")
    with open(json_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    if sort_by == "recall":
        metrics = sorted(metrics, key=lambda x: x["recall"], reverse=True)
    else:
        metrics = sorted(metrics, key=lambda x: x["index"])

    names = [f'{m["folder"]} {m["name"]}' for m in metrics]
    recalls = [m["recall"] for m in metrics]

    fig = go.Figure(data=go.Bar(
        x=names,
        y=recalls,
        marker_color="orange",
        hovertemplate="%{x}<br>Recall: %{y:.3f}<extra></extra>",
    ))

    fig.update_layout(
        title="Per-Class Recall",
        xaxis_title="Flower Class",
        yaxis_title="Recall",
        width=1800,
        height=550,
        xaxis=dict(tickfont=dict(size=7), tickangle=90),
        yaxis=dict(range=[0, 1.05]),
    )

    return fig


def build_training_curves():
    """
    Build a Plotly training-curves figure with dual-subplot layout.
    Left: Loss curves. Right: Accuracy curves.
    Best-epoch marker on the accuracy subplot.
    Uses botanical color scheme matching the Dashboard design.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    history_path = os.path.join(EVAL_DIR, "history.json")

    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            hist = json.load(f)

        epochs = list(range(1, len(hist["train_loss"]) + 1))

        # Find best val-acc epoch
        best_epoch_idx = int(np.argmax(hist["val_acc"]))
        best_epoch = best_epoch_idx + 1
        best_val_acc = hist["val_acc"][best_epoch_idx]

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Loss", "Accuracy"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]],
        )

        # --- Loss subplot (left) ---------------------------------------------
        fig.add_trace(go.Scatter(
            x=epochs, y=hist["train_loss"], mode="lines+markers",
            name="Train Loss",
            line=dict(color="#8fbc8f", width=2),
            marker=dict(size=3, color="#8fbc8f"),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=epochs, y=hist["val_loss"], mode="lines+markers",
            name="Val Loss",
            line=dict(color="#5b8c5a", width=2.2),
            marker=dict(size=3, color="#5b8c5a"),
        ), row=1, col=1)

        # --- Accuracy subplot (right) ----------------------------------------
        fig.add_trace(go.Scatter(
            x=epochs, y=hist["train_acc"], mode="lines+markers",
            name="Train Acc",
            line=dict(color="#8fbc8f", width=2, dash="dot"),
            marker=dict(size=3, color="#8fbc8f"),
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=epochs, y=hist["val_acc"], mode="lines+markers",
            name="Val Acc",
            line=dict(color="#5b8c5a", width=2.2),
            marker=dict(size=3, color="#5b8c5a"),
        ), row=1, col=2)

        # --- Best epoch marker on accuracy subplot ----------------------------
        fig.add_trace(go.Scatter(
            x=[best_epoch], y=[best_val_acc], mode="markers+text",
            name="Best Epoch",
            marker=dict(size=14, color="#d4786e", symbol="star", line=dict(width=1.5, color="#fff")),
            text=[f"Epoch {best_epoch}<br>{best_val_acc:.1f}%"],
            textposition="top center",
            textfont=dict(size=10, color="#d4786e"),
            showlegend=True,
        ), row=1, col=2)

        fig.update_layout(
            title=dict(
                text=f"Training Curves — Best Val Acc: {best_val_acc:.1f}% at Epoch {best_epoch}",
                font=dict(size=14, color="#2d3436"),
            ),
            showlegend=True,
            legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
            width=1050, height=420,
            margin=dict(t=60, b=30, l=40, r=20),
            plot_bgcolor="#faf8f5",
            paper_bgcolor="#fff",
        )
        fig.update_xaxes(title_text="Epoch", row=1, col=1, gridcolor="#ede8e0")
        fig.update_xaxes(title_text="Epoch", row=1, col=2, gridcolor="#ede8e0")
        fig.update_yaxes(title_text="Loss", row=1, col=1, gridcolor="#ede8e0")
        fig.update_yaxes(title_text="Accuracy (%)", row=1, col=2, gridcolor="#ede8e0")

    else:
        # --- Fallback: clean placeholder ------------------------------------
        summary_path = os.path.join(EVAL_DIR, "evaluation_summary.json")

        fig = go.Figure()
        fig.update_layout(
            title=dict(
                text="Training Curves — History data not available",
                font=dict(size=16, color="#2d3436"),
            ),
            width=800, height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(t=60, b=40, l=40, r=40),
        )

        lines = [
            "The per-epoch training history was not persisted by the training script.",
            "To enable interactive curves, save the history dict as evaluation_data/history.json",
        ]
        if os.path.exists(summary_path):
            with open(summary_path) as f:
                s = json.load(f)
            lines.append("")
            lines.append(f"Final test-set accuracy: {s['accuracy']}% "
                         f"({s['correct']} correct / {s['incorrect']} incorrect, "
                         f"{s['num_samples']} images across {s['num_classes']} classes)")

        fig.add_annotation(
            text="<br>".join(lines),
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font=dict(size=13, color="#636e72"),
            align="center",
        )

    return fig


def build_class_misclassification(class_idx: int):
    """
    Build a Plotly bar chart showing which classes a given true class
    is most often misclassified as.

    Parameters
    ----------
    class_idx : int
        The true class index (0-101) to analyze.
    """
    import plotly.graph_objects as go

    json_path = os.path.join(EVAL_DIR, "confusion_matrix.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cm = np.array(data["matrix"])
    row = cm[class_idx, :].copy()
    # Exclude correct predictions (diagonal)
    row[class_idx] = 0
    total_misclass = int(row.sum())

    # Get indices of non-zero misclassifications, sorted
    nonzero = np.where(row > 0)[0]
    if len(nonzero) == 0:
        fig = go.Figure()
        fig.update_layout(
            title=f"No misclassifications for: {FLOWER_NAMES[class_idx]} ({class_idx+1:03d})"
        )
        return fig

    sorted_idx = nonzero[np.argsort(row[nonzero])[::-1]]
    names = [f"{i+1:03d} {FLOWER_NAMES[i]}" for i in sorted_idx]
    counts = [int(row[i]) for i in sorted_idx]

    fig = go.Figure(data=go.Bar(
        x=names,
        y=counts,
        marker_color="coral",
        hovertemplate="%{x}<br>Misclassified as: %{y}<extra></extra>",
    ))

    fig.update_layout(
        title=(
            f'Misclassifications of "{FLOWER_NAMES[class_idx]}" '
            f"({class_idx+1:03d}) — Total errors: {total_misclass}"
        ),
        xaxis_title="Predicted (incorrect) Class",
        yaxis_title="Count",
        width=1400,
        height=500,
        xaxis=dict(tickfont=dict(size=8), tickangle=90),
    )

    return fig


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("Running test-set evaluation …")
    print("=" * 60)
    run_evaluation(save=True)
    print("\nDone. Data saved to evaluation_data/")
