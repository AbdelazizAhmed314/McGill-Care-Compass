"""Safety routing helpers for high-risk intake cases."""

from __future__ import annotations

from dataclasses import dataclass

HIGH_RISK_CATEGORIES = {
    "health_care",
    "mental_health",
    "insurance",
    "immigration_status",
    "housing",
    "tax",
    "finances",
    "work_career",
    "safety_urgent",
}

LIMITATION_TEMPLATES = {
    "health_care": (
        "This navigator can point you to official healthcare starting points, but it "
        "cannot diagnose symptoms, recommend treatment, or decide whether care is urgent."
    ),
    "mental_health": (
        "This navigator can point you to support resources, but it cannot assess risk, "
        "diagnose, or replace crisis or clinical support."
    ),
    "emergency": (
        "If this is an emergency or immediate danger, call 911 or go to the nearest "
        "emergency department. Regular navigator results are secondary."
    ),
    "insurance": (
        "This navigator can link to official insurance resources, but it cannot decide "
        "coverage, reimbursement, exemptions, or claim outcomes."
    ),
    "immigration_status": (
        "This navigator can link to official immigration and student-service resources, "
        "but it cannot interpret documents, decide status, or provide legal advice."
    ),
    "tax": (
        "This navigator can link to CRA and student tax resources, but it cannot decide "
        "tax residency, filing obligations, credits, deductions, or refunds."
    ),
    "finances": (
        "This navigator can link to funding and support resources, but it cannot decide "
        "financial-aid eligibility, award amounts, or application outcomes."
    ),
    "work_career": (
        "This navigator can link to career and official work resources, but it cannot "
        "interpret permit conditions or decide work authorization."
    ),
    "housing": (
        "This navigator can link to housing and tenant-information resources, but it "
        "cannot provide legal advice or decide a dispute."
    ),
    "unsupported": (
        "This navigator does not have source-grounded evidence for that request. It will "
        "not invent a recommendation."
    ),
    "system_error": (
        "The navigator could not complete source-grounded retrieval because a local "
        "system dependency failed. Try again after the app health check passes."
    ),
}

SILVER_DATA_NOTICE = (
    "This result comes from processed Silver RAG evidence that has not been approved as "
    "a final Gold recommendation."
)


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


def limitation_notice_for_category(category_id: str, *, review_status: str = "") -> str:
    """Return category-specific limitation wording for user-facing output."""

    limitations: list[str] = []
    if requires_limitation_notice(category_id):
        limitations.append(
            LIMITATION_TEMPLATES.get(category_id, LIMITATION_TEMPLATES["unsupported"])
        )
    if review_status == "silver_unreviewed":
        limitations.append(SILVER_DATA_NOTICE)
    return " ".join(limitations)


def unsupported_notice() -> str:
    """Return the standard unsupported-scope fallback notice."""

    return LIMITATION_TEMPLATES["unsupported"]


def system_error_notice() -> str:
    """Return the standard safe system-error notice."""

    return LIMITATION_TEMPLATES["system_error"]


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
        return LIMITATION_TEMPLATES["emergency"]
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
