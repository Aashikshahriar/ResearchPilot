from functools import lru_cache

from app.config import get_settings
from app.services.vision.base import VisionProvider
from app.services.vision.heuristic_provider import HeuristicVisionProvider


@lru_cache
def get_vision_provider() -> VisionProvider:
    settings = get_settings()
    if settings.vision_provider == "clip":
        from app.services.vision.clip_provider import CLIPVisionProvider

        return CLIPVisionProvider()
    return HeuristicVisionProvider()
