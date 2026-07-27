"""Privacy-bounded usability records and aggregate Issue 10 metrics."""

from __future__ import annotations

import csv
import json
import re
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
    "limitation_required",
    "limitation_visible",
    "confidence_before",
    "confidence_after",
    "usefulness_rating",
    "critical_issue",
    "issue_severity",
    "task_blocked",
    "issue_status",
    "issue_reference",
    "issue_tags",
)
PARTICIPANT_TYPES = {"target", "proxy"}
BOOLEAN_VALUES = {"true": True, "false": False}
SCENARIO_IDS = {
    "UT01_INSURANCE",
    "UT02_HEALTHCARE",
    "UT03_HOUSING",
    "UT04_DOCUMENTS",
    "UT05_TAX",
}
SCENARIO_LIMITATION_REQUIREMENTS = {
    "UT01_INSURANCE": True,
    "UT02_HEALTHCARE": True,
    "UT03_HOUSING": True,
    "UT04_DOCUMENTS": False,
    "UT05_TAX": True,
}
ISSUE_TAGS = {
    "accessibility",
    "error-recovery",
    "form-flow",
    "limitation-visibility",
    "mobile-layout",
    "navigation",
    "performance",
    "privacy",
    "ranking",
    "safety",
    "source-visibility",
    "wording",
}
ISSUE_SEVERITIES = {"none", "low", "medium", "high", "critical"}
ISSUE_STATUSES = {"none", "open", "documented", "resolved"}
SEVERITY_WEIGHTS = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
SESSION_ID_PATTERN = re.compile(r"U\d{2,3}")
ISSUE_REFERENCE_PATTERN = re.compile(
    r"(?:issue:#\d+|pr:#\d+|commit:[0-9a-f]{7,40}|docs:[a-z0-9][a-z0-9._/-]{0,100})"
)


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
    limitation_required: bool
    limitation_visible: bool
    confidence_before: int
    confidence_after: int
    usefulness_rating: int
    critical_issue: bool
    issue_severity: str
    task_blocked: bool
    issue_status: str
    issue_reference: str
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
    _validate_record_set(records)
    return records


def analyze_usability(records: Sequence[UsabilityRecord]) -> dict[str, Any]:
    """Calculate the Issue 10 measures without exposing participant-level data."""

    records = tuple(records)
    _validate_record_set(records)
    count = len(records)
    completed_records = [record for record in records if record.completed]
    limitation_records = [record for record in records if record.limitation_required]
    confidence_changes = [
        record.confidence_after - record.confidence_before for record in records
    ]
    completion_times = [record.completion_seconds for record in completed_records]
    critical_records = [record for record in records if record.critical_issue]
    unresolved_critical_records = [
        record for record in critical_records if record.issue_status == "open"
    ]
    metrics = {
        "record_count": count,
        "completed_records": len(completed_records),
        "incomplete_records": count - len(completed_records),
        "target_participants": sum(record.participant_type == "target" for record in records),
        "proxy_participants": sum(record.participant_type == "proxy" for record in records),
        "task_completion_rate": _rate(records, "completed"),
        "identified_next_step_rate": _rate(records, "identified_next_step"),
        "relevant_service_top_three_rate": _rate(records, "relevant_service_top_three"),
        "explanation_understood_rate": _rate(records, "explanation_understood"),
        "source_link_visible_rate": _rate(records, "source_link_visible"),
        "limitation_required_records": len(limitation_records),
        "limitation_visible_rate": _rate(limitation_records, "limitation_visible"),
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
        "critical_issue_count": len(critical_records),
        "resolved_or_documented_critical_issue_count": (
            len(critical_records) - len(unresolved_critical_records)
        ),
        "unresolved_critical_issue_count": len(unresolved_critical_records),
    }
    targets = {
        "minimum_completed_records": metrics["completed_records"] >= 5,
        "task_completion": metrics["task_completion_rate"] >= 0.8,
        "identified_next_step": metrics["identified_next_step_rate"] >= 0.8,
        "relevant_service_top_three": metrics["relevant_service_top_three_rate"] >= 0.8,
        "explanation_understood": metrics["explanation_understood_rate"] >= 0.7,
        "source_link_visible": metrics["source_link_visible_rate"] >= 0.8,
        "limitation_visible": (
            metrics["limitation_required_records"] > 0
            and metrics["limitation_visible_rate"] >= 0.8
        ),
        "median_under_two_minutes": (
            metrics["median_completion_seconds"] is not None
            and metrics["median_completion_seconds"] < 120
        ),
        "confidence_improvement": metrics["average_confidence_change"] >= 1.0,
        "usefulness": metrics["average_usefulness_rating"] >= 4.0,
        "no_unresolved_critical_issues": metrics["unresolved_critical_issue_count"] == 0,
    }
    return {
        "report_schema_version": "2",
        "status": "ready" if all(targets.values()) else "needs_attention",
        "metrics": metrics,
        "targets": targets,
        "issue_tag_counts": _issue_tag_counts(records),
        "prioritized_issues": _prioritized_issues(records),
        "recruitment": {
            "target_participant_preferred": metrics["target_participants"] > 0,
            "all_proxy_sample": count > 0 and metrics["target_participants"] == 0,
        },
        "privacy": {
            "validated_record_contract": True,
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
        f"- Total anonymous records: {metrics['record_count']}",
        f"- Completed anonymous records: {metrics['completed_records']}",
        f"- Task-completion rate: {metrics['task_completion_rate']:.1%}",
        f"- Target participants: {metrics['target_participants']}",
        f"- Proxy participants: {metrics['proxy_participants']}",
        f"- Identified-next-step rate: {metrics['identified_next_step_rate']:.1%}",
        f"- Relevant-service rate: {metrics['relevant_service_top_three_rate']:.1%}",
        f"- Explanation-understood rate: {metrics['explanation_understood_rate']:.1%}",
        f"- Official-source visibility rate: {metrics['source_link_visible_rate']:.1%}",
        f"- Required-limitation visibility rate: {metrics['limitation_visible_rate']:.1%}",
        f"- Median completion time: {metrics['median_completion_seconds']}",
        f"- Average confidence change: {metrics['average_confidence_change']}",
        f"- Average usefulness: {metrics['average_usefulness_rating']}/5",
        f"- Critical issues: {metrics['critical_issue_count']}",
        f"- Unresolved critical issues: {metrics['unresolved_critical_issue_count']}",
        "",
        "## Acceptance targets",
        "",
    ]
    lines.extend(
        f"- {'PASS' if passed else 'PENDING/FAIL'}: `{name}`"
        for name, passed in targets.items()
    )
    lines.extend(["", "## Prioritized issue tags", ""])
    prioritized_issues = report.get("prioritized_issues", [])
    if prioritized_issues:
        lines.extend(
            (
                f"- `{issue['tag']}`: severity `{issue['highest_severity']}`, "
                f"{issue['affected_sessions']} affected, "
                f"{issue['blocked_sessions']} blocked, "
                f"{issue['unresolved_critical_sessions']} unresolved critical, "
                f"priority score {issue['priority_score']}"
            )
            for issue in prioritized_issues
        )
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
    scenario_id = str(row["scenario_id"]).strip().upper()
    participant_type = str(row["participant_type"]).strip().lower()
    completion_seconds = _float_value(row, "completion_seconds", row_number)
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
            "limitation_required",
            "limitation_visible",
            "critical_issue",
            "task_blocked",
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
    record = UsabilityRecord(
        session_id=session_id,
        participant_type=participant_type,
        scenario_id=scenario_id,
        completion_seconds=completion_seconds,
        issue_severity=str(row["issue_severity"]).strip().lower(),
        issue_status=str(row["issue_status"]).strip().lower(),
        issue_reference=str(row["issue_reference"]).strip().lower(),
        issue_tags=tags,
        **boolean_fields,
        **ratings,
    )
    _validate_record(record, row_number=row_number)
    return record


def _validate_record_set(records: Sequence[UsabilityRecord]) -> None:
    for index, record in enumerate(records, 2):
        _validate_record(record, row_number=index)
    identifiers = [record.session_id for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Usability session_id values must be unique.")


def _validate_record(record: UsabilityRecord, *, row_number: int) -> None:
    if SESSION_ID_PATTERN.fullmatch(record.session_id) is None:
        raise ValueError(f"Row {row_number} session_id must use study-local form U01-U999.")
    if record.scenario_id not in SCENARIO_IDS:
        raise ValueError(f"Row {row_number} has an unsupported scenario_id.")
    if record.participant_type not in PARTICIPANT_TYPES:
        raise ValueError(f"Row {row_number} has an unsupported participant_type.")
    if not 0 <= record.completion_seconds <= 3600:
        raise ValueError(f"Row {row_number} completion_seconds must be between 0 and 3600.")
    for field in ("confidence_before", "confidence_after", "usefulness_rating"):
        if not 1 <= getattr(record, field) <= 5:
            raise ValueError(f"Row {row_number} field {field} must be between 1 and 5.")
    unknown_tags = set(record.issue_tags) - ISSUE_TAGS
    if unknown_tags:
        raise ValueError(
            f"Row {row_number} has unsupported issue_tags: "
            + ", ".join(sorted(unknown_tags))
        )
    if record.issue_severity not in ISSUE_SEVERITIES:
        raise ValueError(f"Row {row_number} has an unsupported issue_severity.")
    if record.issue_status not in ISSUE_STATUSES:
        raise ValueError(f"Row {row_number} has an unsupported issue_status.")
    if not record.issue_tags:
        if (
            record.issue_severity != "none"
            or record.task_blocked
            or record.critical_issue
            or record.issue_status != "none"
            or record.issue_reference
        ):
            raise ValueError(
                f"Row {row_number} without issue_tags must use the no-issue values."
            )
    else:
        if record.issue_severity == "none" or record.issue_status == "none":
            raise ValueError(
                f"Row {row_number} with issue_tags needs issue_severity and issue_status."
            )
    if (record.issue_severity == "critical") != record.critical_issue:
        raise ValueError(
            f"Row {row_number} critical_issue and issue_severity must agree."
        )
    expected_limitation = SCENARIO_LIMITATION_REQUIREMENTS[record.scenario_id]
    if record.limitation_required != expected_limitation:
        raise ValueError(
            f"Row {row_number} limitation_required does not match the scenario contract."
        )
    if not expected_limitation and record.limitation_visible:
        raise ValueError(
            f"Row {row_number} limitation_visible cannot be true when not required."
        )
    reference_required = (
        record.issue_status in {"documented", "resolved"} or record.critical_issue
    )
    if reference_required and not record.issue_reference:
        raise ValueError(
            f"Row {row_number} needs an issue_reference for this issue status."
        )
    if record.issue_reference and ISSUE_REFERENCE_PATTERN.fullmatch(
        record.issue_reference
    ) is None:
        raise ValueError(f"Row {row_number} has an unsupported issue_reference.")


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


def _prioritized_issues(records: Sequence[UsabilityRecord]) -> list[dict[str, Any]]:
    aggregates: dict[str, dict[str, Any]] = {}
    for record in records:
        for tag in record.issue_tags:
            issue = aggregates.setdefault(
                tag,
                {
                    "tag": tag,
                    "affected_sessions": 0,
                    "blocked_sessions": 0,
                    "critical_sessions": 0,
                    "unresolved_critical_sessions": 0,
                    "highest_severity": "none",
                    "open_sessions": 0,
                    "documented_sessions": 0,
                    "resolved_sessions": 0,
                },
            )
            issue["affected_sessions"] += 1
            issue["blocked_sessions"] += int(record.task_blocked)
            issue["critical_sessions"] += int(record.critical_issue)
            issue["unresolved_critical_sessions"] += int(
                record.critical_issue and record.issue_status == "open"
            )
            issue[f"{record.issue_status}_sessions"] += 1
            if (
                SEVERITY_WEIGHTS[record.issue_severity]
                > SEVERITY_WEIGHTS[issue["highest_severity"]]
            ):
                issue["highest_severity"] = record.issue_severity
    prioritized = []
    for issue in aggregates.values():
        issue["priority_score"] = (
            SEVERITY_WEIGHTS[issue["highest_severity"]] * 100
            + issue["unresolved_critical_sessions"] * 50
            + issue["blocked_sessions"] * 20
            + issue["affected_sessions"]
        )
        prioritized.append(issue)
    return sorted(
        prioritized,
        key=lambda issue: (
            -issue["priority_score"],
            -issue["affected_sessions"],
            issue["tag"],
        ),
    )
