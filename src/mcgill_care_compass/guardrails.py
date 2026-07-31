"""Safety routing helpers shared by every navigator interface."""

from __future__ import annotations

import re
import unicodedata
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

PROMPT_INJECTION_PATTERNS = {
    "instruction_override": re.compile(
        r"\b(?:ignore|disregard|override)\b.{0,80}\b(?:previous|prior|system|developer|"
        r"safety|guardrail|instruction)s?\b|\bbypass\b.{0,40}\b(?:safety|guardrail)s?\b",
        re.IGNORECASE,
    ),
    "prompt_or_secret_extraction": re.compile(
        r"\b(?:reveal|show|print|repeat|expose|leak)\b.{0,80}\b(?:system prompt|developer "
        r"message|hidden instructions?|environment variables?|api keys?|secret)s?\b",
        re.IGNORECASE,
    ),
    "role_manipulation": re.compile(
        r"\b(?:act as|pretend to be|you are now)\b.{0,60}\b(?:dan|unrestricted|unfiltered|"
        r"developer mode|without rules|no restrictions)\b",
        re.IGNORECASE,
    ),
}
SOURCE_FABRICATION_PATTERNS = (
    re.compile(
        r"\b(?:invent|fabricate|make up)\b.{0,80}\b(?:service|source|citation|url|"
        r"link|contact|office)s?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:create|generate|provide|give(?: me)?|write)\b.{0,40}\b(?:a |an |some )?"
        r"(?:fake|fabricated|made-up)\b.{0,40}\b(?:service|source|citation|url|link|contact|"
        r"office)s?\b",
        re.IGNORECASE,
    ),
)
SENSITIVE_VALUE_PATTERN = re.compile(
    r"\b(?:student(?: id(?: number)?| identification(?: number)?| number)|mcgill id|"
    r"social insurance number|sin|passport(?: number)?|medical record(?: number)?)\b"
    r"\s*(?:(?:is)\s+|[:=#]\s*|\s+(?=[a-z0-9-]*\d))"
    r"(?=[a-z0-9-]*\d)[a-z0-9-]{4,}",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OfficialFallbackResource:
    """One governed official starting point for a bounded failure state."""

    label: str
    action: str
    source_url: str


FALLBACK_SOURCE_URLS = {
    "academics": ("McGill academic advising", "https://www.mcgill.ca/students/advising/"),
    "documents_admin": ("McGill Student Records", "https://www.mcgill.ca/student-records/"),
    "finances": ("McGill Scholarships and Student Aid", "https://www.mcgill.ca/studentaid/"),
    "health_care": ("McGill Student Wellness Hub", "https://www.mcgill.ca/wellness-hub/"),
    "mental_health": ("McGill Student Wellness Hub", "https://www.mcgill.ca/wellness-hub/"),
    "insurance": (
        "McGill international student health insurance",
        "https://www.mcgill.ca/internationalstudents/health",
    ),
    "immigration_status": (
        "Government of Canada study permits",
        "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/study-permit.html",
    ),
    "work_career": (
        "Government of Canada work while studying",
        "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/work.html",
    ),
    "tax": (
        "Canada Revenue Agency personal income tax",
        "https://www.canada.ca/en/services/taxes/income-tax/personal-income-tax.html",
    ),
    "housing": ("McGill off-campus housing", "https://www.mcgill.ca/students/housing/offcampus"),
    "language_integration": (
        "McGill language programs",
        "https://www.mcgill.ca/continuingstudies/area-of-study/languages",
    ),
    "safety_urgent": (
        "McGill urgent-care guidance",
        "https://www.mcgill.ca/wellness-hub/get-support/urgent-care",
    ),
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


def limitation_notice_for_category(category_id: str, *, review_status: str = "") -> str:
    """Return category-specific limitation wording for user-facing output."""

    limitations: list[str] = []
    if requires_limitation_notice(category_id):
        template_key = "emergency" if category_id == "safety_urgent" else category_id
        limitations.append(
            LIMITATION_TEMPLATES.get(template_key, LIMITATION_TEMPLATES["unsupported"])
        )
    if review_status == "silver_unreviewed":
        limitations.append(SILVER_DATA_NOTICE)
    return " ".join(limitations)


def limitation_notice(category_id: str) -> str:
    """Compatibility alias for the governed category limitation."""

    return limitation_notice_for_category(category_id)


def unsupported_notice() -> str:
    """Return the standard unsupported-scope fallback notice."""

    return LIMITATION_TEMPLATES["unsupported"]


def system_error_notice() -> str:
    """Return the standard safe system-error notice."""

    return LIMITATION_TEMPLATES["system_error"]


def normalize_guardrail_text(text: str) -> str:
    """Normalize Unicode and invisible formatting before safety matching."""

    normalized = unicodedata.normalize("NFKC", str(text or ""))
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) not in {"Cf", "Cc"} or character.isspace()
    )
    return re.sub(r"\s+", " ", normalized, flags=re.UNICODE).strip()


def _guardrail_text_variants(text: str) -> tuple[str, ...]:
    """Return deterministic punctuation variants for obfuscation-resistant matching."""

    normalized = normalize_guardrail_text(text)
    punctuation_as_space = "".join(
        " " if unicodedata.category(character).startswith("P") else character
        for character in normalized
    )
    punctuation_removed = "".join(
        character for character in normalized if not unicodedata.category(character).startswith("P")
    )
    return tuple(
        dict.fromkeys(
            re.sub(r"\s+", " ", variant, flags=re.UNICODE).strip()
            for variant in (normalized, punctuation_as_space, punctuation_removed)
        )
    )


def adversarial_input_reasons(text: str) -> tuple[str, ...]:
    """Return bounded reason codes for unsafe optional free-text input."""

    variants = _guardrail_text_variants(text)
    reasons = [
        reason
        for reason, pattern in PROMPT_INJECTION_PATTERNS.items()
        if any(pattern.search(variant) for variant in variants)
    ]
    if any(
        pattern.search(variant) for pattern in SOURCE_FABRICATION_PATTERNS for variant in variants
    ):
        reasons.append("source_fabrication")
    if any(SENSITIVE_VALUE_PATTERN.search(variant) for variant in variants):
        reasons.append("sensitive_identifier")
    return tuple(dict.fromkeys(reasons))


def adversarial_evidence_reasons(text: str) -> tuple[str, ...]:
    """Return instruction-like patterns found in retrieved public evidence."""

    variants = _guardrail_text_variants(text)
    return tuple(
        reason
        for reason, pattern in PROMPT_INJECTION_PATTERNS.items()
        if any(pattern.search(variant) for variant in variants)
    )


def official_fallback_resources(category_id: str) -> tuple[OfficialFallbackResource, ...]:
    """Return the official starting point owned by the relevant service context."""

    label, source_url = FALLBACK_SOURCE_URLS.get(
        category_id,
        ("McGill Student Services", "https://www.mcgill.ca/studentservices"),
    )
    return (
        OfficialFallbackResource(
            label=label,
            action=(
                "Use this official starting point to find the responsible service and "
                "verify the next step before acting."
            ),
            source_url=source_url,
        ),
    )


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

    source_name = "McGill Student Wellness Hub urgent-care guidance"
    source_url = "https://www.mcgill.ca/wellness-hub/get-support/urgent-care"
    return (
        EmergencyResource(
            label="Emergency services",
            action="Call 911 if this is an emergency or there is immediate danger.",
            phone="911",
            source_name=source_name,
            source_url=source_url,
            limitation="Use this for immediate danger or emergency situations.",
        ),
        EmergencyResource(
            label="Nearest emergency department",
            action="Go to the nearest emergency department if immediate in-person care is needed.",
            source_name=source_name,
            source_url=source_url,
            limitation="This navigator cannot choose a facility or assess wait times.",
        ),
    )
