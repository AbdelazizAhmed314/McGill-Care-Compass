"""Safety routing helpers for high-risk intake cases."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

HIGH_RISK_CATEGORIES = {
    "health_care",
    "mental_health",
    "insurance",
    "immigration_status",
    "tax",
    "finances",
    "work_career",
    "safety_urgent",
}

CATEGORY_LIMITATIONS = {
    "health_care": (
        "This is navigation information only. Use the official source or a qualified "
        "health professional for personal medical decisions."
    ),
    "mental_health": (
        "This is navigation information only. If there is immediate danger or a crisis, "
        "use emergency or crisis supports instead of relying on this navigator."
    ),
    "insurance": (
        "This does not decide coverage or reimbursement. Confirm details with the "
        "official insurer or McGill office listed in the source."
    ),
    "immigration_status": (
        "This is not legal or immigration advice and does not determine status or "
        "eligibility. Confirm requirements with official immigration sources or a "
        "qualified advisor."
    ),
    "tax": (
        "This is not tax advice and does not determine residency, filing obligations, "
        "deductions, credits, or refunds. Confirm details with official tax sources or "
        "a qualified tax professional."
    ),
    "finances": (
        "This does not decide financial-aid eligibility, award amounts, or application "
        "outcomes. Confirm details with the official source."
    ),
    "work_career": (
        "This does not decide work authorization or interpret permit conditions. Confirm "
        "requirements with official sources or a qualified advisor."
    ),
    "safety_urgent": (
        "Urgent safety concerns should use emergency or crisis supports first; this "
        "navigator should not be used as emergency triage."
    ),
}

GENERAL_LIMITATION = (
    "This is source-grounded navigation information only. Confirm details with the "
    "official source before acting."
)

MCGILL_STUDENT_SERVICES_URL = "https://www.mcgill.ca/studentservices"
MCGILL_URGENT_CARE_URL = "https://www.mcgill.ca/wellness-hub/get-support/urgent-care"
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
    re.compile(
        r"\bfake\b\s+(?:me\s+)?(?:a|an|the)\s+"
        r"(?:service|source|citation|url|link|contact|office)s?\b",
        re.IGNORECASE,
    ),
)
SENSITIVE_VALUE_PATTERN = re.compile(
    r"\b(?:student id|social insurance number|sin|passport(?: number)?|"
    r"medical record(?: number)?)\b\s*(?:is|:|=)\s*[a-z0-9-]{4,}",
    re.IGNORECASE,
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


@dataclass(frozen=True)
class OfficialFallbackResource:
    """One bounded official starting point used when recommendations are unavailable."""

    label: str
    action: str
    source_url: str


def requires_limitation_notice(category_id: str) -> bool:
    """Return whether a category needs explicit limitation wording."""

    return category_id in HIGH_RISK_CATEGORIES


def limitation_notice(category_id: str) -> str:
    """Return the required category-specific boundary for a high-risk topic."""

    if not requires_limitation_notice(category_id):
        return ""
    return CATEGORY_LIMITATIONS.get(category_id, GENERAL_LIMITATION)


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


def adversarial_input_reasons(text: str) -> tuple[str, ...]:
    """Return bounded reason codes for unsafe or adversarial free-text input."""

    variants = _guardrail_text_variants(text)
    reasons = [
        reason
        for reason, pattern in PROMPT_INJECTION_PATTERNS.items()
        if any(pattern.search(variant) for variant in variants)
    ]
    if any(
        pattern.search(variant)
        for pattern in SOURCE_FABRICATION_PATTERNS
        for variant in variants
    ):
        reasons.append("source_fabrication")
    if any(SENSITIVE_VALUE_PATTERN.search(variant) for variant in variants):
        reasons.append("sensitive_identifier")
    return tuple(reasons)


def adversarial_evidence_reasons(text: str) -> tuple[str, ...]:
    """Return prompt-injection reasons found in public retrieved source text."""

    variants = _guardrail_text_variants(text)
    return tuple(
        reason
        for reason, pattern in PROMPT_INJECTION_PATTERNS.items()
        if any(pattern.search(variant) for variant in variants)
    )


def normalize_guardrail_text(text: str) -> str:
    """Normalize Unicode, zero-width characters, and whitespace before matching."""

    normalized = unicodedata.normalize("NFKC", str(text or ""))
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Cf"
    )
    normalized = re.sub(r"\s+", " ", normalized, flags=re.UNICODE)
    return normalized.strip()


def _guardrail_text_variants(text: str) -> tuple[str, ...]:
    """Return bounded punctuation variants without fuzzy or semantic matching."""

    normalized = normalize_guardrail_text(text)
    punctuation_as_space = "".join(
        " " if unicodedata.category(character).startswith("P") else character
        for character in normalized
    )
    punctuation_removed = "".join(
        character
        for character in normalized
        if not unicodedata.category(character).startswith("P")
    )
    return tuple(
        dict.fromkeys(
            re.sub(r"\s+", " ", variant, flags=re.UNICODE).strip()
            for variant in (normalized, punctuation_as_space, punctuation_removed)
        )
    )


def emergency_resources() -> tuple[EmergencyResource, ...]:
    """Return baseline emergency actions that do not depend on RAG retrieval."""

    return (
        EmergencyResource(
            label="Emergency services",
            action="Call 911 if this is an emergency or there is immediate danger.",
            phone="911",
            source_name="McGill Student Wellness Hub urgent-care guidance",
            source_url=MCGILL_URGENT_CARE_URL,
            limitation="Use this for immediate danger or emergency situations.",
        ),
        EmergencyResource(
            label="Nearest emergency department",
            action="Go to the nearest emergency department if immediate in-person care is needed.",
            source_name="McGill Student Wellness Hub urgent-care guidance",
            source_url=MCGILL_URGENT_CARE_URL,
            limitation="This navigator cannot choose a facility or assess wait times.",
        ),
    )


def official_fallback_resources() -> tuple[OfficialFallbackResource, ...]:
    """Return a stable official source when retrieval cannot make a recommendation."""

    return (
        OfficialFallbackResource(
            label="McGill Student Services",
            action=(
                "Use the official Student Services directory to find the responsible office "
                "or service."
            ),
            source_url=MCGILL_STUDENT_SERVICES_URL,
        ),
    )
