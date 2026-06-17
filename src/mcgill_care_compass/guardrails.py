"""Safety routing helpers for high-risk intake cases."""

from __future__ import annotations

HIGH_RISK_CATEGORIES = {
    "health_care",
    "mental_health",
    "insurance",
    "immigration_status",
    "tax",
    "finances",
    "safety_urgent",
}


def requires_limitation_notice(category_id: str) -> bool:
    """Return whether a category needs explicit limitation wording."""

    return category_id in HIGH_RISK_CATEGORIES


def emergency_notice(urgency_level: str | None) -> str | None:
    """Return emergency guidance for urgent intake values."""

    if not urgency_level:
        return None
    normalized = urgency_level.strip().lower()
    if normalized in {"emergency", "immediate danger", "life-threatening"}:
        return (
            "If this is an emergency or immediate safety concern, call 911 or go to the "
            "nearest emergency department."
        )
    return None
