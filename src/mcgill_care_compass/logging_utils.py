"""Privacy-preserving structured runtime logging helpers."""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "mcgill_care_compass.log"

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


def log_event(event: str, **fields: object) -> None:
    """Write one bounded JSON operational event without user-authored text."""

    safe = safe_event_fields(
        event=event,
        timestamp=datetime.now(UTC).isoformat(),
        **fields,
    )
    app_logger().info(json.dumps(safe, ensure_ascii=True, sort_keys=True))


def log_exception(event: str, error: BaseException, **fields: object) -> None:
    """Log only the exception class and allowlisted operational context."""

    log_event(event, error_type=type(error).__name__, **fields)
