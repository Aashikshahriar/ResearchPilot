"""Real LLM provider backed by Google's Gemini API. Also used for PDF/paper
text analysis (summarization, RAG answering, structured comparison) whenever
LLM_PROVIDER=gemini or it appears in LLM_FALLBACK_ORDER -- no separate code
path is needed since paper_service/rag_service/analysis_service all talk to
the LLMProvider abstraction generically.
"""

from typing import Any

import httpx

from app.services.llm.base import EmbeddingResult, LLMProvider, LLMResult, StructuredResult

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def _strip_unsupported_schema_keys(schema: Any) -> Any:
    """Gemini's responseSchema is a restricted subset of OpenAPI/JSON Schema
    that rejects keys like additionalProperties. Recursively strip them."""
    if isinstance(schema, dict):
        return {
            k: _strip_unsupported_schema_keys(v)
            for k, v in schema.items()
            if k not in {"additionalProperties"}
        }
    if isinstance(schema, list):
        return [_strip_unsupported_schema_keys(v) for v in schema]
    return schema


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, chat_model: str, embedding_model: str, timeout: float = 60.0):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required to use the Gemini provider")
        self.api_key = api_key
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self._client = httpx.Client(base_url=GEMINI_BASE_URL, timeout=timeout)

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.2) -> LLMResult:
        payload = {
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": temperature},
        }
        data = self._post(f"/models/{self.chat_model}:generateContent", payload)
        text = self._extract_text(data)
        usage = data.get("usageMetadata", {})
        return LLMResult(
            text=text,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            model=self.chat_model,
        )

    def generate_structured(
        self, system_prompt: str, user_prompt: str, schema: dict[str, Any], *, temperature: float = 0.0
    ) -> StructuredResult:
        import json

        payload = {
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
                "responseSchema": _strip_unsupported_schema_keys(schema),
            },
        }
        data = self._post(f"/models/{self.chat_model}:generateContent", payload)
        text = self._extract_text(data)
        usage = data.get("usageMetadata", {})
        return StructuredResult(
            data=json.loads(text),
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            model=self.chat_model,
        )

    def embed(self, texts: list[str]) -> EmbeddingResult:
        requests = [
            {"model": f"models/{self.embedding_model}", "content": {"parts": [{"text": t}]}} for t in texts
        ]
        data = self._post(f"/models/{self.embedding_model}:batchEmbedContents", {"requests": requests})
        vectors = [item["values"] for item in data.get("embeddings", [])]
        dim = len(vectors[0]) if vectors else 0
        return EmbeddingResult(vectors=vectors, model=self.embedding_model, dim=dim)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.post(path, params={"key": self.api_key}, json=payload)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts)
