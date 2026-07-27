"""Privacy-bounded usability records and aggregate Issue 10 metrics."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any

REQUIRED_FIELDS = (
    "session_id",
    "participant_type",
    "scenario_id",
    "completed",
    "completion_seconds",
    "identified_next_step",
    "relevant_service_top_three",
    "explanation_understood",
    "source_link_visible",
    "limitation_visible",
    "confidence_before",
    "confidence_after",
    "usefulness_rating",
    "critical_issue",
    "issue_tags",
)
PARTICIPANT_TYPES = {"target", "proxy"}
BOOLEAN_VALUES = {"true": True, "false": False}


@dataclass(frozen=True)
class UsabilityRecord:
    """One anonymous participant's primary usability task."""

    session_id: str
    participant_type: str
    scenario_id: str
    completed: bool
    completion_seconds: float
    identified_next_step: bool
    relevant_service_top_three: bool
    explanation_understood: bool
    source_link_visible: bool
    limitation_visible: bool
    confidence_before: int
    confidence_after: int
    usefulness_rating: int
    critical_issue: bool
    issue_tags: tuple[str, ...]


def load_usability_records(path: Path) -> list[UsabilityRecord]:
    """Load a CSV that contains only the approved anonymous fields."""

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = tuple(reader.fieldnames or ())
        missing = set(REQUIRED_FIELDS) - set(headers)
        unexpected = set(headers) - set(REQUIRED_FIELDS)
        if missing or unexpected:
            details = []
            if missing:
                details.append("missing: " + ", ".join(sorted(missing)))
            if unexpected:
                details.append("unexpected: " + ", ".join(sorted(unexpected)))
            raise ValueError("Invalid usability CSV fields (" + "; ".join(details) + ").")
        records = [_parse_record(row, row_number=index) for index, row in enumerate(reader, 2)]
    identifiers = [record.session_id for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Usability session_id values must be unique.")
    return records


def analyze_usability(records: Sequence[UsabilityRecord]) -> dict[str, Any]:
    """Calculate the Issue 10 measures without exposing participant-level data."""

    count = len(records)
    confidence_changes = [
        record.confidence_after - record.confidence_before for record in records
    ]
    completion_times = [record.completion_seconds for record in records if record.completed]
    metrics = {
        "completed_records": count,
        "target_participants": sum(record.participant_type == "target" for record in records),
        "proxy_participants": sum(record.participant_type == "proxy" for record in records),
        "task_completion_rate": _rate(records, "completed"),
        "identified_next_step_rate": _rate(records, "identified_next_step"),
        "relevant_service_top_three_rate": _rate(records, "relevant_service_top_three"),
        "explanation_understood_rate": _rate(records, "explanation_understood"),
        "source_link_visible_rate": _rate(records, "source_link_visible"),
        "limitation_visible_rate": _rate(records, "limitation_visible"),
        "under_two_minutes_rate": (
            round(sum(value < 120 for value in completion_times) / len(completion_times), 4)
            if completion_times
            else 0.0
        ),
        "median_completion_seconds": (
            round(median(completion_times), 2) if completion_times else None
        ),
        "average_confidence_change": (
            round(mean(confidence_changes), 2) if confidence_changes else 0.0
        ),
        "average_usefulness_rating": (
            round(mean(record.usefulness_rating for record in records), 2)
            if records
            else 0.0
        ),
        "critical_issue_count": sum(record.critical_issue for record in records),
    }
    targets = {
        "minimum_records": count >= 5,
        "identified_next_step": metrics["identified_next_step_rate"] >= 0.8,
        "relevant_service_top_three": metrics["relevant_service_top_three_rate"] >= 0.8,
        "explanation_understood": metrics["explanation_understood_rate"] >= 0.7,
        "median_under_two_minutes": (
            metrics["median_completion_seconds"] is not None
            and metrics["median_completion_seconds"] < 120
        ),
        "confidence_improvement": metrics["average_confidence_change"] >= 1.0,
        "usefulness": metrics["average_usefulness_rating"] >= 4.0,
        "no_unresolved_critical_issues": metrics["critical_issue_count"] == 0,
    }
    return {
        "report_schema_version": "1",
        "status": "ready" if all(targets.values()) else "needs_attention",
        "metrics": metrics,
        "targets": targets,
        "issue_tag_counts": _issue_tag_counts(records),
        "privacy": {
            "contains_participant_identifiers": False,
            "participant_level_rows_in_report": False,
        },
    }


def write_usability_reports(
    report: Mapping[str, Any], *, json_path: Path, markdown_path: Path
) -> None:
    """Write aggregate-only Issue 10 evidence."""

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(format_usability_markdown(report), encoding="utf-8")


def format_usability_markdown(report: Mapping[str, Any]) -> str:
    """Render aggregate metrics and prioritized issue tags."""

    metrics = report["metrics"]
    targets = report["targets"]
    lines = [
        "# Issue 10 Usability Findings",
        "",
        f"- Status: `{report['status']}`",
        f"- Completed anonymous records: {metrics['completed_records']}",
        f"- Target participants: {metrics['target_participants']}",
        f"- Proxy participants: {metrics['proxy_participants']}",
        f"- Identified-next-step rate: {metrics['identified_next_step_rate']:.1%}",
        f"- Relevant-service rate: {metrics['relevant_service_top_three_rate']:.1%}",
        f"- Explanation-understood rate: {metrics['explanation_understood_rate']:.1%}",
        f"- Median completion time: {metrics['median_completion_seconds']}",
        f"- Average confidence change: {metrics['average_confidence_change']}",
        f"- Average usefulness: {metrics['average_usefulness_rating']}/5",
        f"- Critical issues: {metrics['critical_issue_count']}",
        "",
        "## Acceptance targets",
        "",
    ]
    lines.extend(
        f"- {'PASS' if passed else 'PENDING/FAIL'}: `{name}`"
        for name, passed in targets.items()
    )
    lines.extend(["", "## Prioritized issue tags", ""])
    tag_counts = report.get("issue_tag_counts", {})
    if tag_counts:
        lines.extend(f"- `{tag}`: {count}" for tag, count in tag_counts.items())
    else:
        lines.append("- No issue tags recorded.")
    lines.extend(
        [
            "",
            "## Privacy note",
            "",
            "This report contains aggregate measures only. The source CSV must not contain "
            "names, emails, student IDs, detailed health information, immigration identifiers, "
            "or verbatim participant quotations.",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_record(row: Mapping[str, str], *, row_number: int) -> UsabilityRecord:
    session_id = str(row["session_id"]).strip()
    scenario_id = str(row["scenario_id"]).strip()
    participant_type = str(row["participant_type"]).strip().lower()
    if not session_id or not scenario_id:
        raise ValueError(f"Row {row_number} needs session_id and scenario_id.")
    if participant_type not in PARTICIPANT_TYPES:
        raise ValueError(f"Row {row_number} has an unsupported participant_type.")
    completion_seconds = _float_value(row, "completion_seconds", row_number)
    if completion_seconds < 0 or completion_seconds > 3600:
        raise ValueError(f"Row {row_number} completion_seconds must be between 0 and 3600.")
    ratings = {
        field: _rating_value(row, field, row_number)
        for field in ("confidence_before", "confidence_after", "usefulness_rating")
    }
    boolean_fields = {
        field: _boolean_value(row, field, row_number)
        for field in (
            "completed",
            "identified_next_step",
            "relevant_service_top_three",
            "explanation_understood",
            "source_link_visible",
            "limitation_visible",
            "critical_issue",
        )
    }
    tags = tuple(
        sorted(
            {
                tag.strip().lower()
                for tag in str(row["issue_tags"]).split("|")
                if tag.strip()
            }
        )
    )
    return UsabilityRecord(
        session_id=session_id,
        participant_type=participant_type,
        scenario_id=scenario_id,
        completion_seconds=completion_seconds,
        issue_tags=tags,
        **boolean_fields,
        **ratings,
    )


def _boolean_value(row: Mapping[str, str], field: str, row_number: int) -> bool:
    value = str(row[field]).strip().lower()
    if value not in BOOLEAN_VALUES:
        raise ValueError(f"Row {row_number} field {field} must be true or false.")
    return BOOLEAN_VALUES[value]


def _rating_value(row: Mapping[str, str], field: str, row_number: int) -> int:
    try:
        value = int(str(row[field]).strip())
    except ValueError as error:
        raise ValueError(f"Row {row_number} field {field} must be an integer.") from error
    if not 1 <= value <= 5:
        raise ValueError(f"Row {row_number} field {field} must be between 1 and 5.")
    return value


def _float_value(row: Mapping[str, str], field: str, row_number: int) -> float:
    try:
        return float(str(row[field]).strip())
    except ValueError as error:
        raise ValueError(f"Row {row_number} field {field} must be numeric.") from error


def _rate(records: Sequence[UsabilityRecord], field: str) -> float:
    if not records:
        return 0.0
    passed = sum(bool(getattr(record, field)) for record in records)
    return round(passed / len(records), 4)


def _issue_tag_counts(records: Sequence[UsabilityRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        for tag in record.issue_tags:
            counts[tag] = counts.get(tag, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
