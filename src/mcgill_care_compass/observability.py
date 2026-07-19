"""Privacy-safe application logging and runtime health helpers."""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LOGGER_NAME = "mcgill_care_compass"
SENSITIVE_KEYS = {
    "query",
    "student_need",
    "student_id",
    "sin",
    "social_insurance_number",
    "passport",
    "passport_number",
    "medical_details",
    "medical_record",
    "medical_record_number",
}
SAFE_CONTEXT_KEYS = {
    "stage",
    "category_id",
    "urgency_level",
    "status",
    "error_type",
    "scenario_id",
}
SAFE_CONTEXT_VALUES = {
    "stage": {"retrieval", "llm_response"},
    "category_id": {
        "health_care",
        "mental_health",
        "insurance",
        "immigration_status",
        "housing",
        "academics",
        "finances",
        "work_career",
        "tax",
        "documents_admin",
        "language_integration",
        "safety_urgent",
    },
    "urgency_level": {
        "routine",
        "urgent_not_emergency",
        "urgent but not emergency",
        "emergency",
        "emergency_immediate_danger",
        "immediate danger",
        "life-threatening",
        "planning_ahead",
        "unsure",
    },
    "status": {
        "matched",
        "emergency",
        "unsafe_input",
        "unsupported",
        "no_match",
        "low_confidence",
        "system_error",
    },
}
SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")


class JsonFormatter(logging.Formatter):
    """Render one compact JSON object per log event."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        context = getattr(record, "safe_context", None)
        if isinstance(context, dict):
            payload["context"] = sanitize_context(context)
        if record.exc_info:
            payload["exception_type"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=True, sort_keys=True)


def configure_logging(level: str | None = None) -> logging.Logger:
    """Configure the project logger once and return it."""

    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger
    configured_level = (level or os.getenv("MCC_LOG_LEVEL", "INFO")).upper()
    logger.setLevel(getattr(logging, configured_level, logging.INFO))
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def sanitize_context(context: dict[str, Any]) -> dict[str, Any]:
    """Keep only bounded operational fields, never arbitrary user-authored values."""

    sanitized: dict[str, Any] = {}
    for key, value in context.items():
        normalized_key = str(key).casefold()
        if normalized_key in SENSITIVE_KEYS or normalized_key not in SAFE_CONTEXT_KEYS:
            continue
        if not isinstance(value, (str, int, float, bool, type(None))):
            continue
        if normalized_key in SAFE_CONTEXT_VALUES:
            normalized_value = str(value or "").casefold()
            sanitized[normalized_key] = (
                normalized_value
                if normalized_value in SAFE_CONTEXT_VALUES[normalized_key]
                else "unknown"
            )
        elif isinstance(value, str) and not SAFE_IDENTIFIER_RE.fullmatch(value):
            sanitized[normalized_key] = "unknown"
        else:
            sanitized[normalized_key] = value
    return sanitized


def log_runtime_error(
    error: Exception,
    *,
    stage: str,
    category_id: str = "",
    urgency_level: str = "",
) -> None:
    """Log an operational failure without recording free text or identifiers."""

    logger = configure_logging()
    logger.error(
        "Navigator operation failed",
        exc_info=(type(error), error, error.__traceback__),
        extra={
            "safe_context": {
                "stage": stage,
                "category_id": category_id,
                "urgency_level": urgency_level,
                "error_type": type(error).__name__,
            }
        },
    )


def file_health(path: Path) -> dict[str, Any]:
    """Return a serializable existence/size check for a required runtime artifact."""

    return {
        "path": str(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }
