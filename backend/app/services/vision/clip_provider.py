"""Real zero-shot figure classification using a pretrained CLIP model via
HuggingFace transformers. Requires the optional heavy dependencies in
requirements-vision.txt (torch + transformers). Enable with
VISION_PROVIDER=clip.
"""

from functools import lru_cache

from app.services.vision.base import FIGURE_LABEL_PROMPTS, FIGURE_LABELS, ClassificationResult, VisionProvider

CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"


@lru_cache
def _load_model():
    import torch
    from transformers import CLIPModel, CLIPProcessor

    model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
    model.eval()
    return model, processor, torch


class CLIPVisionProvider(VisionProvider):
    name = CLIP_MODEL_NAME

    def classify(self, image_path: str) -> ClassificationResult:
        from PIL import Image

        model, processor, torch = _load_model()
        image = Image.open(image_path).convert("RGB")
        prompts = [FIGURE_LABEL_PROMPTS[label] for label in FIGURE_LABELS]

        inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]

        best_idx = int(probs.argmax())
        return ClassificationResult(
            label=FIGURE_LABELS[best_idx],
            confidence=round(float(probs[best_idx]), 4),
            model_name=self.name,
        )

    def describe(self, image_path: str, label: str, caption: str | None = None) -> str:
        human_label = label.replace("_", " ")
        base = f"A {human_label} extracted from the paper."
        if caption:
            base += f' The original caption reads: "{caption.strip()[:400]}"'
        return base
