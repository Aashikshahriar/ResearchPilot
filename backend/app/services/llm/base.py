from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResult:
    text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    model: str = ""


@dataclass
class StructuredResult:
    data: dict[str, Any]
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    model: str = ""


@dataclass
class EmbeddingResult:
    vectors: list[list[float]]
    model: str = ""
    dim: int = 0


class LLMProvider(ABC):
    """Abstraction over a chat/completion + embedding backend.

    Swapping the underlying AI vendor should only require implementing this
    interface and selecting it via LLM_PROVIDER — no other application code
    should talk to a vendor SDK directly.
    """

    name: str = "base"

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.2) -> LLMResult:
        """Free-form text generation."""

    @abstractmethod
    def generate_structured(
        self, system_prompt: str, user_prompt: str, schema: dict[str, Any], *, temperature: float = 0.0
    ) -> StructuredResult:
        """Generation constrained to a JSON schema, returned as a parsed dict."""

    @abstractmethod
    def embed(self, texts: list[str]) -> EmbeddingResult:
        """Embed a batch of texts into vectors."""
