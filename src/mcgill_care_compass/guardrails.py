"""Safety routing helpers for high-risk intake cases."""

from __future__ import annotations

from dataclasses import dataclass

HIGH_RISK_CATEGORIES = {
    "health_care",
    "mental_health",
    "insurance",
    "immigration_status",
    "tax",
    "finances",
    "safety_urgent",
}


@dataclass(frozen=True)
class EmergencyResource:
    """One baseline emergency action shown without normal retrieval."""

    label: str
    action: str
    phone: str = ""
    source_name: str = ""
    source_url: str = ""
    limitation: str = ""


def requires_limitation_notice(category_id: str) -> bool:
    """Return whether a category needs explicit limitation wording."""

    return category_id in HIGH_RISK_CATEGORIES


def emergency_notice(urgency_level: str | None) -> str | None:
    """Return emergency guidance for urgent intake values."""

    if not urgency_level:
        return None
    normalized = urgency_level.strip().lower()
    if normalized in {
        "emergency",
        "emergency_immediate_danger",
        "immediate danger",
        "life-threatening",
    }:
        return (
            "If this is an emergency or immediate safety concern, call 911 or go to the "
            "nearest emergency department."
        )
    return None


def emergency_resources() -> tuple[EmergencyResource, ...]:
    """Return baseline emergency actions that do not depend on RAG retrieval."""

    return (
        EmergencyResource(
            label="Emergency services",
            action="Call 911 if this is an emergency or there is immediate danger.",
            phone="911",
            limitation="Use this for immediate danger or emergency situations.",
        ),
        EmergencyResource(
            label="Nearest emergency department",
            action="Go to the nearest emergency department if immediate in-person care is needed.",
            limitation="This navigator cannot choose a facility or assess wait times.",
        ),
    )
