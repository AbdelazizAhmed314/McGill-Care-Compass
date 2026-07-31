"""Reusable contextual ranking helpers for source-grounded RAG chunks."""

from __future__ import annotations

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

DEFAULT_LICENCE_OR_TERMS = "allows_non_commercial_or_link_and_paraphrase"

SOURCE_GROUP_PRIORITY = {
    "canada": 10,
    "quebec": 20,
    "healthcare_system": 30,
    "mcgill": 40,
    "official_open_data": 50,
    "trusted_community": 60,
    "community": 70,
    "external": 80,
    "unknown": 90,
}

SOURCE_GROUP_ALIASES = {
    "canada.ca": "canada",
    "canada": "canada",
    "canada revenue agency": "canada",
    "cra": "canada",
    "federal": "canada",
    "official_federal": "canada",
    "quebec.ca": "quebec",
    "quebec": "quebec",
    "qu?bec": "quebec",
    "gouvernement du qu?bec": "quebec",
    "gouvernement du quebec": "quebec",
    "official_provincial": "quebec",
    "healthcare system": "healthcare_system",
    "healthcare_system": "healthcare_system",
    "health system": "healthcare_system",
    "ramq": "healthcare_system",
    "ciusss": "healthcare_system",
    "sante montreal": "healthcare_system",
    "sant? montr?al": "healthcare_system",
    "official_health_system": "healthcare_system",
    "mcgill": "mcgill",
    "mcgill university": "mcgill",
    "official_university": "mcgill",
    "odhf": "official_open_data",
    "official open data": "official_open_data",
    "official_open_data": "official_open_data",
    "trusted community": "trusted_community",
    "trusted_community": "trusted_community",
    "community": "community",
}

CONTEXTUAL_AUTHORITY_ORDER = {
    "academics": ("mcgill", "quebec", "canada", "trusted_community", "community"),
    "documents_admin": ("mcgill", "quebec", "canada", "trusted_community", "community"),
    "finances": ("mcgill", "quebec", "canada", "trusted_community", "community"),
    "health_care": ("healthcare_system", "mcgill", "quebec", "canada", "trusted_community"),
    "mental_health": ("healthcare_system", "mcgill", "quebec", "trusted_community", "community"),
    "insurance": ("healthcare_system", "quebec", "mcgill", "canada", "trusted_community"),
    "immigration_status": ("canada", "quebec", "mcgill", "trusted_community", "community"),
    "work_career": ("canada", "mcgill", "quebec", "trusted_community", "community"),
    "tax": ("canada", "quebec", "mcgill", "trusted_community", "community"),
    "housing": ("quebec", "mcgill", "trusted_community", "community", "canada"),
    "language_integration": ("mcgill", "quebec", "trusted_community", "community", "canada"),
    "safety_urgent": ("healthcare_system", "quebec", "mcgill", "canada", "trusted_community"),
}

JURISDICTION_SOURCE_GROUP = {"mcgill": "mcgill", "quebec": "quebec", "canada": "canada"}


def normalize_source_group(
    source_group: str = "",
    *,
    authority_level: str = "",
    source_publisher: str = "",
    domain: str = "",
) -> str:
    """Normalize source labels to stable source groups."""

    for candidate in (source_group, authority_level, source_publisher, domain):
        folded = str(candidate or "").strip().casefold()
        if not folded:
            continue
        if folded in SOURCE_GROUP_ALIASES:
            return SOURCE_GROUP_ALIASES[folded]
        if "canada.ca" in folded or "revenue agency" in folded:
            return "canada"
        if "quebec.ca" in folded or "qu?bec" in folded or "quebec" in folded:
            return "quebec"
        if any(value in folded for value in ("ramq", "ciusss", "sante", "sant?")):
            return "healthcare_system"
        if "mcgill" in folded:
            return "mcgill"
    return "unknown"


def source_priority_rank(
    source_group: str = "",
    *,
    authority_level: str = "",
    source_publisher: str = "",
    domain: str = "",
) -> int:
    """Return the legacy global source rank stored as corpus metadata."""

    normalized = normalize_source_group(
        source_group,
        authority_level=authority_level,
        source_publisher=source_publisher,
        domain=domain,
    )
    return SOURCE_GROUP_PRIORITY.get(normalized, SOURCE_GROUP_PRIORITY["unknown"])


def contextual_source_rank(
    metadata: dict[str, Any], *, category_id: str = "", jurisdiction: str = ""
) -> int:
    """Rank authority according to the service owner relevant to this intake."""

    source_group = normalize_source_group(
        str(metadata.get("source_group", "")),
        authority_level=str(metadata.get("authority_level", "")),
        source_publisher=str(metadata.get("source_publisher", "")),
        domain=str(metadata.get("domain", "")),
    )
    order = list(CONTEXTUAL_AUTHORITY_ORDER.get(category_id, ()))
    jurisdiction_group = JURISDICTION_SOURCE_GROUP.get(jurisdiction.strip().casefold())
    if jurisdiction_group:
        order = [jurisdiction_group, *(group for group in order if group != jurisdiction_group)]
    if source_group in order:
        return order.index(source_group) * 10
    return 80 + SOURCE_GROUP_PRIORITY.get(source_group, SOURCE_GROUP_PRIORITY["unknown"])


def parse_datetime(value: Any) -> datetime | None:
    """Parse common ISO and HTTP date formats into aware UTC datetimes."""

    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(text)
        except (TypeError, ValueError, IndexError, OverflowError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def freshness_score(
    *, source_updated_at: Any = "", retrieved_at: Any = "", now: datetime | None = None
) -> float:
    """Return a higher-is-fresher score in the 0..1 range."""

    reference = parse_datetime(source_updated_at) or parse_datetime(retrieved_at)
    if reference is None:
        return 0.0
    now = (now or datetime.now(UTC)).astimezone(UTC)
    age_days = max((now - reference).total_seconds() / 86_400, 0.0)
    return round(1.0 / (1.0 + (age_days / 30.0)), 6)


def ranking_metadata(metadata: dict[str, Any]) -> dict[str, str]:
    """Build ranking fields persisted on pages and chunks."""

    source_group = normalize_source_group(
        str(metadata.get("source_group", "")),
        authority_level=str(metadata.get("authority_level", "")),
        source_publisher=str(metadata.get("source_publisher", "")),
        domain=str(metadata.get("domain", "")),
    )
    return {
        "source_group": source_group,
        "source_priority_rank": str(source_priority_rank(source_group)),
        "freshness_score": str(
            freshness_score(
                source_updated_at=metadata.get("source_updated_at", ""),
                retrieved_at=metadata.get("retrieved_at", ""),
            )
        ),
    }


def retrieved_chunk_sort_key(
    candidate: dict[str, Any], *, category_id: str = "", jurisdiction: str = ""
) -> tuple[int, float, float, str, str, str]:
    """Sort by contextual authority, relevance, freshness, and stable identifiers."""

    metadata = candidate.get("metadata", candidate) or {}
    source_rank = contextual_source_rank(
        metadata, category_id=category_id, jurisdiction=jurisdiction
    )
    try:
        freshness = float(metadata.get("freshness_score", ""))
    except (TypeError, ValueError):
        freshness = freshness_score(
            source_updated_at=metadata.get("source_updated_at", ""),
            retrieved_at=metadata.get("retrieved_at", ""),
        )
    try:
        distance = float(candidate.get("distance", 0.0))
    except (TypeError, ValueError):
        distance = float("inf")
    canonical_url = str(metadata.get("canonical_url", metadata.get("url", ""))).casefold()
    stable_id = str(
        metadata.get("chunk_id") or metadata.get("vector_id") or candidate.get("id", "")
    ).casefold()
    document = str(candidate.get("document", "")).casefold()
    return source_rank, distance, -freshness, canonical_url, stable_id, document


def rank_retrieved_chunks(
    candidates: list[dict[str, Any]], *, category_id: str = "", jurisdiction: str = ""
) -> list[dict[str, Any]]:
    """Rank chunks with contextual project authority and relevance rules."""

    return sorted(
        candidates,
        key=lambda candidate: retrieved_chunk_sort_key(
            candidate, category_id=category_id, jurisdiction=jurisdiction
        ),
    )
