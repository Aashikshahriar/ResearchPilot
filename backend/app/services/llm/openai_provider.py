import json
from typing import Any

import httpx

from app.services.llm.base import EmbeddingResult, LLMProvider, LLMResult, StructuredResult

OPENAI_BASE_URL = "https://api.openai.com/v1"


class OpenAIProvider(LLMProvider):
    """Real LLM provider backed by the OpenAI Chat Completions + Embeddings APIs."""

    name = "openai"

    def __init__(self, api_key: str, chat_model: str, embedding_model: str, timeout: float = 60.0):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        self.api_key = api_key
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self._client = httpx.Client(base_url=OPENAI_BASE_URL, timeout=timeout)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.2) -> LLMResult:
        payload = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        resp = self._client.post("/chat/completions", headers=self._headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return LLMResult(
            text=text,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            model=self.chat_model,
        )

    def generate_structured(
        self, system_prompt: str, user_prompt: str, schema: dict[str, Any], *, temperature: float = 0.0
    ) -> StructuredResult:
        payload = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "response", "schema": schema, "strict": True},
            },
        }
        resp = self._client.post("/chat/completions", headers=self._headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return StructuredResult(
            data=json.loads(content),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            model=self.chat_model,
        )

    def embed(self, texts: list[str]) -> EmbeddingResult:
        payload = {"model": self.embedding_model, "input": texts}
        resp = self._client.post("/embeddings", headers=self._headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()
        vectors = [item["embedding"] for item in data["data"]]
        dim = len(vectors[0]) if vectors else 0
        return EmbeddingResult(vectors=vectors, model=self.embedding_model, dim=dim)
