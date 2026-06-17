"""Transparent rule-based matching scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from mcgill_care_compass.guardrails import requires_limitation_notice
from mcgill_care_compass.schema import ServiceRecord


@dataclass(frozen=True)
class Intake:
    """Minimal structured intake used by the scaffold matcher."""

    main_need: str
    urgency_level: str | None = None
    student_type: str | None = None
    location: str | None = None
    language_preference: str | None = None


@dataclass(frozen=True)
class MatchResult:
    """Ranked match with a traceable reason."""

    record: ServiceRecord
    score: int
    match_reason: str
    limitation_required: bool


def rank_records(intake: Intake, records: list[ServiceRecord], limit: int = 3) -> list[MatchResult]:
    """Rank records with a simple transparent category/name match.

    This is intentionally minimal scaffolding. Issue 4 owns the production matching rules.
    """

    query = intake.main_need.strip().lower()
    results: list[MatchResult] = []
    for record in records:
        haystack = " ".join(
            value or ""
            for value in (
                record.category_id,
                record.category_label,
                record.student_need,
                record.service_name,
            )
        ).lower()
        score = 2 if query == record.category_id.lower() else 0
        if query and query in haystack:
            score += 1
        if score:
            results.append(
                MatchResult(
                    record=record,
                    score=score,
                    match_reason=f"Matched on need/category: {intake.main_need}",
                    limitation_required=requires_limitation_notice(record.category_id),
                )
            )
    return sorted(results, key=lambda result: (-result.score, result.record.service_name))[:limit]
