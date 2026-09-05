"""Dependency-light vision provider used when VISION_PROVIDER=mock (the
default). It performs real image analysis with Pillow/numpy -- color
palette, edge density, aspect ratio -- and maps those measurable features to
a figure class via simple, explainable rules. It is not a neural classifier,
but it genuinely inspects each image rather than returning a canned label.

Swap VISION_PROVIDER=clip (see clip_provider.py) for a real pretrained
zero-shot vision-language model.
"""

import numpy as np
from PIL import Image

from app.services.vision.base import ClassificationResult, VisionProvider


class HeuristicVisionProvider(VisionProvider):
    name = "heuristic-cv"

    def _features(self, image_path: str) -> dict:
        img = Image.open(image_path).convert("RGB")
        arr = np.asarray(img.resize((256, 256))).astype(np.float32)
        gray = arr.mean(axis=2)

        width, height = img.size
        aspect_ratio = width / max(height, 1)

        # Edge density via simple gradient magnitude (Sobel-ish finite differences).
        gx = np.abs(np.diff(gray, axis=1))
        gy = np.abs(np.diff(gray, axis=0))
        edge_density = (gx.mean() + gy.mean()) / 255.0

        # Colorfulness: std across channels (low = grayscale/line-art, high = photo).
        channel_std = arr.reshape(-1, 3).std(axis=0).mean()

        # Fraction of near-white background (common in diagrams/plots/tables).
        white_fraction = float((gray > 235).mean())

        # Fraction of near-black pixels (line art / text-heavy figures).
        dark_fraction = float((gray < 60).mean())

        return dict(
            aspect_ratio=aspect_ratio,
            edge_density=float(edge_density),
            channel_std=float(channel_std),
            white_fraction=white_fraction,
            dark_fraction=dark_fraction,
        )

    def classify(self, image_path: str) -> ClassificationResult:
        f = self._features(image_path)
        scores = {
            "table": 0.0,
            "graph_plot": 0.0,
            "flowchart": 0.0,
            "architecture_diagram": 0.0,
            "mathematical_figure": 0.0,
            "microscopy_image": 0.0,
            "other": 0.15,
        }

        if f["white_fraction"] > 0.55 and f["edge_density"] < 0.05:
            scores["table"] += 0.55
        if f["white_fraction"] > 0.4 and 0.02 < f["edge_density"] < 0.12 and f["channel_std"] < 25:
            scores["graph_plot"] += 0.5
        if f["white_fraction"] > 0.5 and f["edge_density"] >= 0.06 and f["channel_std"] < 30:
            scores["flowchart"] += 0.45
            scores["architecture_diagram"] += 0.35
        if f["dark_fraction"] > 0.02 and f["channel_std"] < 20 and f["white_fraction"] > 0.6:
            scores["mathematical_figure"] += 0.3
        if f["channel_std"] > 35:
            scores["microscopy_image"] += 0.5
            scores["other"] += 0.2
        if 0.9 < f["aspect_ratio"] < 1.6 and f["channel_std"] > 40:
            scores["microscopy_image"] += 0.15

        label = max(scores, key=scores.get)
        total = sum(scores.values()) or 1.0
        confidence = round(min(0.97, max(0.35, scores[label] / total + 0.25)), 2)

        return ClassificationResult(label=label, confidence=confidence, model_name=self.name)

    def describe(self, image_path: str, label: str, caption: str | None = None) -> str:
        f = self._features(image_path)
        human_label = label.replace("_", " ")
        parts = [f"This figure was classified as a {human_label} based on its visual structure."]
        if f["white_fraction"] > 0.5:
            parts.append("It has a predominantly white/light background, typical of a rendered diagram or plot.")
        if f["edge_density"] > 0.08:
            parts.append("High edge density suggests dense line-work, boxes, or text elements.")
        if f["channel_std"] > 35:
            parts.append("Rich color variation suggests photographic or heat-map style content.")
        if caption:
            parts.append(f"Caption context: \"{caption.strip()[:300]}\"")
        return " ".join(parts)
