import time
import uuid
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.models.ai_inference import AIInference


@contextmanager
def log_inference(db: Session, *, operation: str, provider: str, model: str, user_id: uuid.UUID | None = None):
    """Records latency, success/failure, and (when set on the yielded holder)
    token usage / confidence for one AI call, without coupling callers to the
    persistence details."""

    start = time.perf_counter()
    record = {"prompt_tokens": None, "completion_tokens": None, "confidence": None}
    success = True
    error_message = None
    try:
        yield record
    except Exception as exc:  # noqa: BLE001 - we re-raise after logging
        success = False
        error_message = str(exc)[:2000]
        raise
    finally:
        latency_ms = int((time.perf_counter() - start) * 1000)
        db.add(
            AIInference(
                user_id=user_id,
                operation=operation,
                provider=provider,
                model=model,
                latency_ms=latency_ms,
                prompt_tokens=record.get("prompt_tokens"),
                completion_tokens=record.get("completion_tokens"),
                confidence=record.get("confidence"),
                success=success,
                error_message=error_message,
            )
        )
        db.commit()
