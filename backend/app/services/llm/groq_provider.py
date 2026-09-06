import json
from typing import Any

import httpx

from app.services.llm.base import EmbeddingResult, LLMProvider, LLMResult, StructuredResult

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqProvider(LLMProvider):
    """Groq's OpenAI-compatible chat API. Groq does not offer an embeddings
    endpoint, so embed() always raises -- callers using a fallback chain
    should skip to the next provider (or the mock provider) for embeddings."""

    name = "groq"

    def __init__(self, api_key: str, chat_model: str, timeout: float = 60.0):
        if not api_key:
            raise ValueError("GROQ_API_KEY is required to use the Groq provider")
        self.api_key = api_key
        self.chat_model = chat_model
        self._client = httpx.Client(base_url=GROQ_BASE_URL, timeout=timeout)

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
            text=text, prompt_tokens=usage.get("prompt_tokens"), completion_tokens=usage.get("completion_tokens"),
            model=self.chat_model,
        )

    def generate_structured(
        self, system_prompt: str, user_prompt: str, schema: dict[str, Any], *, temperature: float = 0.0
    ) -> StructuredResult:
        schema_instruction = (
            f"{system_prompt}\n\nRespond with a single JSON object matching exactly this JSON schema "
            f"(no extra keys, no markdown fences):\n{json.dumps(schema)}"
        )
        payload = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": schema_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
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
        raise NotImplementedError("Groq does not provide an embeddings API")
