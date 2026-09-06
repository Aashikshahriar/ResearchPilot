import logging
from functools import lru_cache

from app.config import get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.fallback_provider import FallbackLLMProvider
from app.services.llm.mock_provider import MockLLMProvider

logger = logging.getLogger(__name__)


def _build_provider(name: str, settings) -> LLMProvider | None:
    """Instantiate a single named provider, or None if it isn't configured
    (missing API key). Never raises -- the caller decides what to do with a
    missing provider."""
    try:
        if name == "openai":
            if not settings.openai_api_key:
                return None
            from app.services.llm.openai_provider import OpenAIProvider

            return OpenAIProvider(settings.openai_api_key, settings.openai_chat_model, settings.openai_embedding_model)
        if name == "gemini":
            if not settings.gemini_api_key:
                return None
            from app.services.llm.gemini_provider import GeminiProvider

            return GeminiProvider(settings.gemini_api_key, settings.gemini_chat_model, settings.gemini_embedding_model)
        if name == "mistral":
            if not settings.mistral_api_key:
                return None
            from app.services.llm.mistral_provider import MistralProvider

            return MistralProvider(settings.mistral_api_key, settings.mistral_chat_model, settings.mistral_embedding_model)
        if name == "groq":
            if not settings.groq_api_key:
                return None
            from app.services.llm.groq_provider import GroqProvider

            return GroqProvider(settings.groq_api_key, settings.groq_chat_model)
        if name == "mock":
            return MockLLMProvider(embedding_dim=settings.embedding_dim)
    except Exception:
        logger.exception("Failed to construct LLM provider %s", name)
        return None
    return None


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()

    if settings.llm_fallback_order.strip():
        names = [n.strip() for n in settings.llm_fallback_order.split(",") if n.strip()]
        if "mock" not in names:
            names.append("mock")  # guaranteed-available last resort

        chain: list[tuple[str, LLMProvider]] = []
        for name in names:
            provider = _build_provider(name, settings)
            if provider is not None:
                chain.append((name, provider))
            else:
                logger.info("Skipping LLM provider '%s' in fallback chain: not configured", name)

        return FallbackLLMProvider(chain, embedding_dim=settings.embedding_dim)

    provider = _build_provider(settings.llm_provider, settings)
    if provider is not None:
        return provider

    logger.warning("LLM_PROVIDER='%s' is not usable (missing key?) -- falling back to mock", settings.llm_provider)
    return MockLLMProvider(embedding_dim=settings.embedding_dim)
