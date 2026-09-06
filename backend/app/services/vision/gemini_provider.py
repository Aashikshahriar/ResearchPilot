"""Real figure classification + description using Gemini's multimodal
generateContent endpoint (image + text in, structured JSON out). Enabled
with VISION_PROVIDER=gemini and GEMINI_API_KEY set.
"""

import base64
import json
import mimetypes

import httpx

from app.services.vision.base import FIGURE_LABELS, ClassificationResult, VisionProvider

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": FIGURE_LABELS},
        "confidence": {"type": "number"},
        "description": {"type": "string"},
    },
    "required": ["label", "confidence", "description"],
}

CLASSIFY_PROMPT = (
    "You are analyzing a figure extracted from an academic paper. Classify it into exactly one of these "
    f"categories: {', '.join(FIGURE_LABELS)}. Then write a 1-3 sentence factual description of what the "
    "figure actually shows. Respond with confidence as a number between 0 and 1 reflecting how certain "
    "you are of the classification."
)


class GeminiVisionProvider(VisionProvider):
    name = "gemini-vision"

    def __init__(self, api_key: str, model: str, timeout: float = 60.0):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required to use the Gemini vision provider")
        self.api_key = api_key
        self.model = model
        self._client = httpx.Client(base_url=GEMINI_BASE_URL, timeout=timeout)

    def _analyze(self, image_path: str, caption: str | None) -> dict:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        mime_type = mimetypes.guess_type(image_path)[0] or "image/png"

        prompt = CLASSIFY_PROMPT
        if caption:
            prompt += f'\n\nThe figure\'s original caption is: "{caption.strip()[:400]}"'

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}},
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json",
                "responseSchema": CLASSIFY_SCHEMA,
            },
        }
        resp = self._client.post(f"/models/{self.model}:generateContent", params={"key": self.api_key}, json=payload)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)

    def classify(self, image_path: str) -> ClassificationResult:
        result = self._analyze(image_path, caption=None)
        label = result.get("label", "other")
        if label not in FIGURE_LABELS:
            label = "other"
        confidence = float(result.get("confidence", 0.5))
        return ClassificationResult(label=label, confidence=max(0.0, min(1.0, confidence)), model_name=self.model)

    def describe(self, image_path: str, label: str, caption: str | None = None) -> str:
        result = self._analyze(image_path, caption=caption)
        return result.get("description", f"A {label.replace('_', ' ')} extracted from the paper.")
