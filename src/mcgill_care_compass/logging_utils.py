"""Privacy-preserving structured runtime logging helpers."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "mcgill_care_compass.log"
_REQUEST_ID: ContextVar[str] = ContextVar("mcc_request_id", default="")

_ALLOWED_FIELDS = {
    "event",
    "timestamp",
    "status",
    "category_id",
    "urgency_level",
    "error_code",
    "error_type",
    "stage",
    "failed_checks",
    "pages",
    "links",
    "chunks",
    "recommendation_count",
    "duration_ms",
    "request_id",
    "client_type",
    "route",
    "corpus_signature",
    "attention_count",
    "severity",
    "attempt",
    "model",
    "generation_mode",
    "fallback_reason_code",
    "validation_reason_code",
    "openai_request_id",
    "openai_response_id",
    "option_count",
    "approved_chunk_count",
    "llm_attempts",
}


def app_logger() -> logging.Logger:
    """Return one JSON-line logger for stderr and the ignored local log file."""

    logger = logging.getLogger("mcgill_care_compass")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter("%(message)s")
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger


def safe_event_fields(**fields: object) -> dict[str, str]:
    """Return only explicitly allowlisted, non-empty operational fields."""

    safe: dict[str, str] = {}
    for key, value in fields.items():
        if key not in _ALLOWED_FIELDS or value in {None, ""}:
            continue
        safe[key] = str(value)
    return safe


def bind_request_id(request_id: str) -> Token[str]:
    """Bind a privacy-safe correlation ID to the current request context."""

    return _REQUEST_ID.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    """Restore the previous request correlation context."""

    _REQUEST_ID.reset(token)


def current_request_id() -> str:
    """Return the current correlation ID, if one is bound."""

    return _REQUEST_ID.get()


def log_event(event: str, **fields: object) -> None:
    """Write one bounded JSON operational event without user-authored text."""

    fields.setdefault("request_id", current_request_id())
    safe = safe_event_fields(
        event=event,
        timestamp=datetime.now(UTC).isoformat(),
        **fields,
    )
    app_logger().info(json.dumps(safe, ensure_ascii=True, sort_keys=True))


def log_exception(event: str, error: BaseException, **fields: object) -> None:
    """Log only the exception class and allowlisted operational context."""

    log_event(event, error_type=type(error).__name__, **fields)
