"""Reusable ranking helpers for source-grounded RAG chunks."""

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
    "québec": "quebec",
    "gouvernement du québec": "quebec",
    "gouvernement du quebec": "quebec",
    "official_provincial": "quebec",
    "healthcare system": "healthcare_system",
    "healthcare_system": "healthcare_system",
    "health system": "healthcare_system",
    "ramq": "healthcare_system",
    "ciusss": "healthcare_system",
    "sante montreal": "healthcare_system",
    "santé montréal": "healthcare_system",
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


def normalize_source_group(
    source_group: str = "",
    *,
    authority_level: str = "",
    source_publisher: str = "",
    domain: str = "",
) -> str:
    """Normalize source labels to the stable source groups used for ranking."""

    candidates = [source_group, authority_level, source_publisher, domain]
    for candidate in candidates:
        folded = str(candidate or "").strip().casefold()
        if not folded:
            continue
        if folded in SOURCE_GROUP_ALIASES:
            return SOURCE_GROUP_ALIASES[folded]
        if "canada.ca" in folded or "revenue agency" in folded:
            return "canada"
        if "quebec.ca" in folded or "québec" in folded or "quebec" in folded:
            return "quebec"
        if "ramq" in folded or "ciusss" in folded or "sante" in folded or "santé" in folded:
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
    """Return a lower-is-better source rank.

    The project-specific preference order is:
    Canada, Quebec, official healthcare systems, McGill, then other sources.
    """

    normalized = normalize_source_group(
        source_group,
        authority_level=authority_level,
        source_publisher=source_publisher,
        domain=domain,
    )
    return SOURCE_GROUP_PRIORITY.get(normalized, SOURCE_GROUP_PRIORITY["unknown"])


def parse_datetime(value: Any) -> datetime | None:
    """Parse common ISO and HTTP date formats into an aware UTC datetime."""

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
    *,
    source_updated_at: Any = "",
    retrieved_at: Any = "",
    now: datetime | None = None,
) -> float:
    """Return a higher-is-fresher score in the 0..1 range."""

    reference = parse_datetime(source_updated_at) or parse_datetime(retrieved_at)
    if reference is None:
        return 0.0
    now = (now or datetime.now(UTC)).astimezone(UTC)
    age_days = max((now - reference).total_seconds() / 86_400, 0.0)
    return round(1.0 / (1.0 + (age_days / 30.0)), 6)


def ranking_metadata(metadata: dict[str, Any]) -> dict[str, str]:
    """Build ranking fields that can be persisted on pages or chunks."""

    source_group = normalize_source_group(
        str(metadata.get("source_group", "")),
        authority_level=str(metadata.get("authority_level", "")),
        source_publisher=str(metadata.get("source_publisher", "")),
        domain=str(metadata.get("domain", "")),
    )
    return {
        "source_group": source_group,
        "source_priority_rank": str(
            source_priority_rank(
                source_group,
                authority_level=str(metadata.get("authority_level", "")),
                source_publisher=str(metadata.get("source_publisher", "")),
                domain=str(metadata.get("domain", "")),
            )
        ),
        "freshness_score": str(
            freshness_score(
                source_updated_at=metadata.get("source_updated_at", ""),
                retrieved_at=metadata.get("retrieved_at", ""),
            )
        ),
    }


def retrieved_chunk_sort_key(candidate: dict[str, Any]) -> tuple[int, float, float]:
    """Sort key for Chroma candidates: source authority, freshness, then distance."""

    metadata = candidate.get("metadata", candidate) or {}
    priority = metadata.get("source_priority_rank", "")
    try:
        source_rank = int(priority)
    except (TypeError, ValueError):
        source_rank = source_priority_rank(
            str(metadata.get("source_group", "")),
            authority_level=str(metadata.get("authority_level", "")),
            source_publisher=str(metadata.get("source_publisher", "")),
            domain=str(metadata.get("domain", "")),
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
        distance = 0.0
    return source_rank, -freshness, distance


def rank_retrieved_chunks(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank retrieved chunks with the project source preference contract."""

    return sorted(candidates, key=retrieved_chunk_sort_key)
