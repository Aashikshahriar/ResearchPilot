import logging
from functools import lru_cache

from app.config import get_settings
from app.services.vision.base import VisionProvider
from app.services.vision.heuristic_provider import HeuristicVisionProvider

logger = logging.getLogger(__name__)


@lru_cache
def get_vision_provider() -> VisionProvider:
    settings = get_settings()

    if settings.vision_provider == "clip":
        from app.services.vision.clip_provider import CLIPVisionProvider

        return CLIPVisionProvider()

    if settings.vision_provider == "gemini":
        if not settings.gemini_api_key:
            logger.warning("VISION_PROVIDER=gemini but GEMINI_API_KEY is not set -- falling back to heuristic")
            return HeuristicVisionProvider()
        from app.services.vision.gemini_provider import GeminiVisionProvider

        return GeminiVisionProvider(settings.gemini_api_key, settings.gemini_vision_model)

    return HeuristicVisionProvider()
