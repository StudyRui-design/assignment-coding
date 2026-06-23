# -*- coding: utf-8 -*-
"""
Flask web application for the 102-Flowers Classification Demo.

Routes:
  GET  /                    — upload form
  POST /                    — upload + predict
  GET  /training            — training curves page
  GET  /confusion           — confusion matrix interactive page
  GET  /batch               — batch prediction visualization
  GET  /test_image/<path>   — serve test-set images for batch page
  GET  /api/misclass/<idx>  — JSON/HTML misclassification detail
"""

import os
import json
import uuid
import random
import torch
from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

from inference import predict_single, load_model, get_all_class_names
from charts import (
    build_confusion_matrix_heatmap,
    build_recall_chart,
    build_training_curves,
    build_class_misclassification,
)
from flower_names import FLOWER_NAMES
from config import Config

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(__file__), "static", "uploads"
)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
EVAL_DIR = os.path.join(os.path.dirname(__file__), "evaluation_data")


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Routes — Upload & Predict
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    filename = None
    top5_data = None
    all_probs_table = None

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            file.save(save_path)

            image = Image.open(save_path).convert("RGB")
            pred = predict_single(image, return_top_k=5)

            result = {
                "predicted_name": pred["predicted_name"],
                "confidence": f"{pred['confidence']:.2%}",
                "predicted_idx": pred["predicted_idx"],
            }

            top5_data = list(zip(
                pred["top_k_names"],
                [f"{p:.2%}" for p in pred["top_k_probs"]],
                pred["top_k_probs"],
            ))

            probs_with_names = [
                (FLOWER_NAMES[i], float(pred["all_probs"][i]))
                for i in range(102)
            ]
            probs_with_names.sort(key=lambda x: x[1], reverse=True)
            all_probs_table = [
                {"rank": r, "name": name, "prob": f"{p:.4%}"}
                for r, (name, p) in enumerate(probs_with_names, 1)
            ]

            filename = unique_name

    return render_template(
        "index.html",
        result=result,
        filename=filename,
        top5_data=top5_data,
        all_probs_table=all_probs_table,
    )


# ---------------------------------------------------------------------------
# Routes — Training Curves
# ---------------------------------------------------------------------------
@app.route("/training")
def training():
    fig = build_training_curves()
    chart_html = fig.to_html(full_html=False, include_plotlyjs=False)

    # --- Load evaluation data ------------------------------------------------
    summary = {}
    summary_path = os.path.join(EVAL_DIR, "evaluation_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            summary = json.load(f)

    # --- Per-class metrics (sorted by recall, for Chart.js) -------------------
    per_class = []
    pcm_path = os.path.join(EVAL_DIR, "per_class_metrics.json")
    if os.path.exists(pcm_path):
        with open(pcm_path, "r") as f:
            per_class = json.load(f)

    # --- Top confusions (with image paths) ------------------------------------
    top_confusions = []
    tc_path = os.path.join(EVAL_DIR, "top_confusions.json")
    if os.path.exists(tc_path):
        with open(tc_path, "r") as f:
            top_confusions = json.load(f)

    # --- Load predictions (needed for image paths + misclass examples) ----------
    predictions = []
    pred_path = os.path.join(EVAL_DIR, "predictions.json")
    if os.path.exists(pred_path):
        with open(pred_path, "r") as f:
            predictions = json.load(f)

    # Build class→representative-image mapping from real predictions
    class_image_map = {}
    if predictions:
        for p in predictions:
            tl = p["true_label"]
            if tl not in class_image_map:
                class_image_map[tl] = p["path"]

    # --- 100% Recall classes → image cards ------------------------------------
    recall_100 = []
    if per_class and class_image_map:
        for m in per_class:
            if m["recall"] >= 1.0:
                img_path = class_image_map.get(m["index"], "")
                recall_100.append({
                    "name": m["name"],
                    "folder": m["folder"],
                    "recall": m["recall"],
                    "precision": m["precision"],
                    "f1": m["f1"],
                    "img": img_path,
                })

    # --- Low recall classes + misclassified examples --------------------------
    low_recall_cards = []
    if per_class and predictions:
        # Get bottom-6 classes by recall
        sorted_by_recall = sorted(per_class, key=lambda x: x["recall"])
        low_candidates = [m for m in sorted_by_recall if m["recall"] < 0.3][:6]

        for m in low_candidates:
            idx = m["index"]
            mis_examples = [
                p for p in predictions
                if p["true_label"] == idx and not p["correct"]
            ][:4]
            # Most common wrong prediction for this class
            wrong_counts = {}
            for p in mis_examples:
                wrong_counts[p["pred_name"]] = wrong_counts.get(p["pred_name"], 0) + 1
            top_wrong = sorted(wrong_counts.items(), key=lambda x: -x[1])
            example_pred_name = top_wrong[0][0] if top_wrong else "N/A"
            example_pred_label = None
            for p in mis_examples:
                if p["pred_name"] == example_pred_name:
                    example_pred_label = p["pred_label"]
                    break

            # Representative image from the wrongly-predicted class (for contrast)
            pred_class_img = class_image_map.get(example_pred_label, "") if example_pred_label is not None else ""

            low_recall_cards.append({
                "index": idx,
                "folder": m["folder"],
                "name": m["name"],
                "recall": m["recall"],
                "precision": m["precision"],
                "mis_count": len([p for p in predictions
                                  if p["true_label"] == idx and not p["correct"]]),
                "top_wrong_name": example_pred_name,
                "pred_class_img": pred_class_img,
                "examples": mis_examples,
            })

    return render_template(
        "training.html",
        chart_html=chart_html,
        summary=summary,
        per_class=per_class,
        top_confusions=top_confusions,
        recall_100=recall_100,
        low_recall_cards=low_recall_cards,
    )


# ---------------------------------------------------------------------------
# Routes — Confusion Matrix
# ---------------------------------------------------------------------------
@app.route("/confusion")
def confusion():
    fig_cm = build_confusion_matrix_heatmap()
    cm_html = fig_cm.to_html(full_html=False, include_plotlyjs=False)

    fig_recall = build_recall_chart(sort_by="recall")
    recall_html = fig_recall.to_html(full_html=False, include_plotlyjs=False)

    class_options = [
        {"index": i, "label": f"{i+1:03d} - {FLOWER_NAMES[i]}"}
        for i in range(102)
    ]

    summary_path = os.path.join(EVAL_DIR, "evaluation_summary.json")
    summary = {}
    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            summary = json.load(f)

    return render_template(
        "confusion.html",
        cm_html=cm_html,
        recall_html=recall_html,
        class_options=class_options,
        summary=summary,
    )


@app.route("/api/misclass/<int:class_idx>")
def api_misclass(class_idx: int):
    if not 0 <= class_idx < 102:
        return "<p>Invalid class index</p>", 400
    fig = build_class_misclassification(class_idx)
    return fig.to_html(full_html=False, include_plotlyjs=False)


# ---------------------------------------------------------------------------
# Routes — Batch Prediction
# ---------------------------------------------------------------------------
@app.route("/test_image/<path:subpath>")
def serve_test_image(subpath: str):
    """Serve an image file from the test-set directory."""
    cfg = Config()
    return send_from_directory(cfg.test_dir, subpath)


@app.route("/batch")
def batch():
    from torchvision import datasets

    cfg = Config()
    load_model()  # ensure loaded

    test_dataset = datasets.ImageFolder(cfg.test_dir)
    indices = random.sample(range(len(test_dataset)), 8)
    batch_data = []

    for idx in indices:
        img_path, true_label = test_dataset.samples[idx]
        rel_path = os.path.relpath(img_path, cfg.test_dir).replace("\\", "/")
        img = Image.open(img_path).convert("RGB")
        pred = predict_single(img, return_top_k=1)

        batch_data.append({
            "image_url": url_for("serve_test_image", subpath=rel_path),
            "true_name": FLOWER_NAMES[true_label],
            "pred_name": pred["predicted_name"],
            "confidence": f"{pred['confidence']:.2%}",
            "correct": true_label == pred["predicted_idx"],
        })

    return render_template("batch.html", batch_data=batch_data)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Loading model (one-time) ...")
    load_model()
    print("Model ready.")
    print("Starting Flask at http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
