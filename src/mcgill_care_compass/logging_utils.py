"""Minimal privacy-preserving runtime logging helpers."""

from __future__ import annotations

import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "mcgill_care_compass.log"

_SENSITIVE_KEYS = {
    "query",
    "student_id",
    "sin",
    "passport",
    "medical_record",
    "policy_number",
    "claim",
    "income",
    "free_text",
    "description",
}


def app_logger() -> logging.Logger:
    """Return the app logger, creating a local ignored log file if needed."""

    logger = logging.getLogger("mcgill_care_compass")
    logger.setLevel(logging.INFO)
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger


def safe_event_fields(**fields: object) -> dict[str, str]:
    """Return log fields with sensitive values and empty fields removed."""

    safe: dict[str, str] = {}
    for key, value in fields.items():
        normalized_key = key.lower()
        if any(sensitive in normalized_key for sensitive in _SENSITIVE_KEYS):
            continue
        if value in {None, ""}:
            continue
        safe[key] = str(value)
    return safe


def log_event(event: str, **fields: object) -> None:
    """Write one privacy-preserving operational event."""

    safe = safe_event_fields(event=event, **fields)
    message = " ".join(f"{key}={value}" for key, value in safe.items())
    app_logger().info(message)
