"""Grounded explanation formatting."""

from __future__ import annotations

from mcgill_care_compass.matching import MatchResult


def format_recommendation(result: MatchResult) -> str:
    """Format a concise recommendation using only matched record fields."""

    record = result.record
    parts = [
        f"Service: {record.service_name}",
        f"Why this matched: {result.match_reason}",
    ]
    if record.recommended_next_step:
        parts.append(f"Suggested next step: {record.recommended_next_step}")
    if record.official_source_url:
        parts.append(f"Official source: {record.official_source_url}")
    if result.limitation_required and record.limitations:
        parts.append(f"Limitations: {record.limitations}")
    return "\n".join(parts)
