import logging
from typing import Any

from app.services.llm.base import EmbeddingResult, LLMProvider, LLMResult, StructuredResult

logger = logging.getLogger(__name__)


def _normalize_dim(vector: list[float], target_dim: int) -> list[float]:
    """Truncate or zero-pad an embedding to a fixed length.

    Different providers return different native dimensions (Gemini
    text-embedding-004 -> 768, Mistral-embed -> 1024, OpenAI -> 1536). The
    pgvector column has one fixed dimension set at migration time, so every
    embedding -- regardless of which provider produced it -- is normalized
    to that length. This is a pragmatic approximation, not a lossless
    projection: cosine similarity across chunks embedded by different
    providers will be less precise than a single consistent embedding model.
    For best retrieval quality, keep one embedding-capable provider healthy
    rather than relying on the fallback chain to switch mid-run.
    """
    if len(vector) == target_dim:
        return vector
    if len(vector) > target_dim:
        return vector[:target_dim]
    return vector + [0.0] * (target_dim - len(vector))


class FallbackLLMProvider(LLMProvider):
    """Tries a list of (name, provider) pairs in order for generate/
    generate_structured, falling through to the next on any exception.
    Embeddings are normalized to a fixed dimension so pgvector storage stays
    consistent no matter which underlying provider actually served a given
    request. The mock provider should always be last in the chain so there
    is a guaranteed-available final fallback.
    """

    name = "fallback"

    def __init__(self, providers: list[tuple[str, LLMProvider]], embedding_dim: int):
        if not providers:
            raise ValueError("FallbackLLMProvider requires at least one provider")
        self.providers = providers
        self.embedding_dim = embedding_dim

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.2) -> LLMResult:
        last_error: Exception | None = None
        for provider_name, provider in self.providers:
            try:
                result = provider.generate(system_prompt, user_prompt, temperature=temperature)
                result.model = f"{provider_name}:{result.model}"
                return result
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM provider %s failed for generate(): %s", provider_name, exc)
                last_error = exc
        raise RuntimeError(f"All LLM providers failed: {last_error}") from last_error

    def generate_structured(
        self, system_prompt: str, user_prompt: str, schema: dict[str, Any], *, temperature: float = 0.0
    ) -> StructuredResult:
        last_error: Exception | None = None
        for provider_name, provider in self.providers:
            try:
                result = provider.generate_structured(system_prompt, user_prompt, schema, temperature=temperature)
                result.model = f"{provider_name}:{result.model}"
                return result
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM provider %s failed for generate_structured(): %s", provider_name, exc)
                last_error = exc
        raise RuntimeError(f"All LLM providers failed: {last_error}") from last_error

    def embed(self, texts: list[str]) -> EmbeddingResult:
        last_error: Exception | None = None
        for provider_name, provider in self.providers:
            try:
                result = provider.embed(texts)
                vectors = [_normalize_dim(v, self.embedding_dim) for v in result.vectors]
                return EmbeddingResult(vectors=vectors, model=f"{provider_name}:{result.model}", dim=self.embedding_dim)
            except NotImplementedError:
                continue
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM provider %s failed for embed(): %s", provider_name, exc)
                last_error = exc
        raise RuntimeError(f"All LLM providers failed to embed: {last_error}") from last_error
