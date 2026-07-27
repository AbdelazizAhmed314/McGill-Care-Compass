"""Privacy-bounded usability records and aggregate Issue 10 metrics."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
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
)
FINDING_FIELDS = (
    "finding_id",
    "issue_tag",
    "severity",
    "task_blocked",
    "critical",
    "status",
    "reference",
    "affected_session_ids",
)
PARTICIPANT_TYPES = {"target", "proxy"}
BOOLEAN_VALUES = {"true": True, "false": False}
SCENARIO_LIMITATION_REQUIREMENTS = {
    "UT01_INSURANCE": True,
    "UT02_HEALTHCARE": True,
    "UT03_HOUSING": True,
    "UT04_DOCUMENTS": False,
    "UT05_TAX": True,
}
SCENARIO_IDS = frozenset(SCENARIO_LIMITATION_REQUIREMENTS)
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
ISSUE_SEVERITIES = {"low", "medium", "high", "critical"}
ISSUE_STATUSES = {"open", "documented", "resolved"}
SEVERITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
SESSION_ID_PATTERN = re.compile(r"U\d{2,3}")
FINDING_ID_PATTERN = re.compile(r"F\d{2,3}")
OPEN_REFERENCE_PATTERN = re.compile(r"(?:issue|pr):#\d+")
DOCUMENT_REFERENCE_PATTERN = re.compile(r"docs:[a-z0-9][a-z0-9._/-]{0,100}")
COMMIT_REFERENCE_PATTERN = re.compile(r"commit:[0-9a-f]{7,40}")
DIRECT_IDENTIFIER_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:student|passport|medical record|sin)\s*(?:id|number|#)", re.IGNORECASE),
    re.compile(r"\b\d{8,}\b"),
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
    limitation_visible: bool
    confidence_before: int
    confidence_after: int
    usefulness_rating: int


@dataclass(frozen=True)
class UsabilityFinding:
    """One controlled issue with finding-level severity and disposition."""

    finding_id: str
    issue_tag: str
    severity: str
    task_blocked: bool
    critical: bool
    status: str
    reference: str
    affected_session_ids: tuple[str, ...]


def load_usability_records(path: Path) -> list[UsabilityRecord]:
    """Load a CSV that contains only the approved anonymous session fields."""

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_headers(tuple(reader.fieldnames or ()), REQUIRED_FIELDS, "session")
        records = [_parse_record(row, row_number=index) for index, row in enumerate(reader, 2)]
    _validate_record_set(records)
    return records


def load_usability_findings(
    path: Path,
    records: Sequence[UsabilityRecord],
    *,
    repository_root: Path = ROOT,
) -> list[UsabilityFinding]:
    """Load controlled finding rows and verify their local evidence references."""

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_headers(tuple(reader.fieldnames or ()), FINDING_FIELDS, "finding")
        findings = [
            _parse_finding(row, row_number=index) for index, row in enumerate(reader, 2)
        ]
    _validate_finding_set(findings, records, repository_root=repository_root)
    return findings


def load_proxy_justification(path: Path) -> str | None:
    """Return a content hash for a privacy-safe proxy-only recruitment rationale."""

    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8").strip()
    if len(content) < 40:
        raise ValueError("Proxy recruitment justification must contain a substantive rationale.")
    if any(pattern.search(content) for pattern in DIRECT_IDENTIFIER_PATTERNS):
        raise ValueError("Proxy recruitment justification contains a direct identifier pattern.")
    return hashlib.sha256(content.encode()).hexdigest()


def analyze_usability(
    records: Sequence[UsabilityRecord],
    findings: Sequence[UsabilityFinding] = (),
    *,
    proxy_justification_sha256: str | None = None,
) -> dict[str, Any]:
    """Calculate the Issue 10 measures without exposing participant-level data."""

    records = tuple(records)
    findings = tuple(findings)
    _validate_record_set(records)
    _validate_finding_set(findings, records, repository_root=ROOT, verify_references=False)
    count = len(records)
    completed_records = [record for record in records if record.completed]
    limitation_records = [
        record
        for record in records
        if SCENARIO_LIMITATION_REQUIREMENTS[record.scenario_id]
    ]
    confidence_changes = [
        record.confidence_after - record.confidence_before for record in records
    ]
    completion_times = [record.completion_seconds for record in completed_records]
    critical_findings = [finding for finding in findings if finding.critical]
    unresolved_critical_findings = [
        finding for finding in critical_findings if finding.status == "open"
    ]
    scenario_counts = {
        scenario_id: sum(
            record.scenario_id == scenario_id for record in completed_records
        )
        for scenario_id in sorted(SCENARIO_IDS)
    }
    target_participants = sum(record.participant_type == "target" for record in records)
    proxy_participants = sum(record.participant_type == "proxy" for record in records)
    all_proxy_sample = count > 0 and target_participants == 0
    metrics = {
        "record_count": count,
        "completed_records": len(completed_records),
        "incomplete_records": count - len(completed_records),
        "target_participants": target_participants,
        "proxy_participants": proxy_participants,
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
        "finding_count": len(findings),
        "critical_issue_count": len(critical_findings),
        "resolved_or_documented_critical_issue_count": (
            len(critical_findings) - len(unresolved_critical_findings)
        ),
        "unresolved_critical_issue_count": len(unresolved_critical_findings),
    }
    targets = {
        "minimum_completed_records": metrics["completed_records"] >= 5,
        "scenario_coverage": all(scenario_counts.values()),
        "target_or_justified_proxy_sample": (
            count > 0
            and (
                target_participants > 0
                or (all_proxy_sample and proxy_justification_sha256 is not None)
            )
        ),
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
        "report_schema_version": "3",
        "status": "ready" if all(targets.values()) else "needs_attention",
        "metrics": metrics,
        "targets": targets,
        "scenario_counts": scenario_counts,
        "issue_tag_counts": _issue_tag_counts(findings),
        "prioritized_issues": _prioritized_issues(findings),
        "recruitment": {
            "target_participant_preferred": target_participants > 0,
            "all_proxy_sample": all_proxy_sample,
            "proxy_justification_sha256": proxy_justification_sha256,
        },
        "privacy": {
            "validated_record_contract": True,
            "direct_identifiers_rejected": True,
            "participant_level_rows_in_report": False,
        },
    }


def write_usability_reports(
    report: Mapping[str, Any], *, json_path: Path, markdown_path: Path
) -> None:
    """Write aggregate-only Issue 10 evidence."""

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(_json_report(report), encoding="utf-8")
    markdown_path.write_text(format_usability_markdown(report), encoding="utf-8")


def verify_usability_reports(
    report: Mapping[str, Any], *, json_path: Path, markdown_path: Path
) -> None:
    """Reject missing or stale aggregate evidence without rewriting it."""

    if not json_path.exists() or json_path.read_text(encoding="utf-8") != _json_report(report):
        raise ValueError("Committed usability JSON is missing or stale.")
    expected_markdown = format_usability_markdown(report)
    if (
        not markdown_path.exists()
        or markdown_path.read_text(encoding="utf-8") != expected_markdown
    ):
        raise ValueError("Committed usability Markdown is missing or stale.")


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
        f"- Controlled findings: {metrics['finding_count']}",
        f"- Critical issues: {metrics['critical_issue_count']}",
        f"- Unresolved critical issues: {metrics['unresolved_critical_issue_count']}",
        "",
        "## Scenario coverage",
        "",
    ]
    lines.extend(
        f"- `{scenario_id}`: {count}"
        for scenario_id, count in report["scenario_counts"].items()
    )
    lines.extend(["", "## Acceptance targets", ""])
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
                f"{issue['blocked_findings']} blocked findings, "
                f"{issue['unresolved_critical_findings']} unresolved critical findings, "
                f"priority score {issue['priority_score']}"
            )
            for issue in prioritized_issues
        )
    else:
        lines.append("- No issue findings recorded.")
    lines.extend(
        [
            "",
            "## Privacy note",
            "",
            "This report contains aggregate measures only. The source CSVs reject "
            "unapproved fields and direct-identifier patterns; they must not contain "
            "names, emails, student IDs, detailed health information, immigration "
            "identifiers, or verbatim participant quotations.",
            "",
        ]
    )
    return "\n".join(lines)


def _json_report(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def _validate_headers(
    headers: tuple[str, ...], expected: tuple[str, ...], record_type: str
) -> None:
    missing = set(expected) - set(headers)
    unexpected = set(headers) - set(expected)
    if missing or unexpected:
        details = []
        if missing:
            details.append("missing: " + ", ".join(sorted(missing)))
        if unexpected:
            details.append("unexpected: " + ", ".join(sorted(unexpected)))
        raise ValueError(
            f"Invalid usability {record_type} CSV fields (" + "; ".join(details) + ")."
        )


def _parse_record(row: Mapping[str, str], *, row_number: int) -> UsabilityRecord:
    record = UsabilityRecord(
        session_id=str(row["session_id"]).strip(),
        participant_type=str(row["participant_type"]).strip().lower(),
        scenario_id=str(row["scenario_id"]).strip().upper(),
        completion_seconds=_float_value(row, "completion_seconds", row_number),
        **{
            field: _boolean_value(row, field, row_number)
            for field in (
                "completed",
                "identified_next_step",
                "relevant_service_top_three",
                "explanation_understood",
                "source_link_visible",
                "limitation_visible",
            )
        },
        **{
            field: _rating_value(row, field, row_number)
            for field in ("confidence_before", "confidence_after", "usefulness_rating")
        },
    )
    _validate_record(record, row_number=row_number)
    return record


def _parse_finding(row: Mapping[str, str], *, row_number: int) -> UsabilityFinding:
    finding = UsabilityFinding(
        finding_id=str(row["finding_id"]).strip().upper(),
        issue_tag=str(row["issue_tag"]).strip().lower(),
        severity=str(row["severity"]).strip().lower(),
        task_blocked=_boolean_value(row, "task_blocked", row_number),
        critical=_boolean_value(row, "critical", row_number),
        status=str(row["status"]).strip().lower(),
        reference=str(row["reference"]).strip().lower(),
        affected_session_ids=tuple(
            sorted(
                {
                    value.strip().upper()
                    for value in str(row["affected_session_ids"]).split("|")
                    if value.strip()
                }
            )
        ),
    )
    _validate_finding(finding, row_number=row_number)
    return finding


def _validate_record_set(records: Sequence[UsabilityRecord]) -> None:
    for index, record in enumerate(records, 2):
        _validate_record(record, row_number=index)
    identifiers = [record.session_id for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Usability session_id values must be unique.")


def _validate_finding_set(
    findings: Sequence[UsabilityFinding],
    records: Sequence[UsabilityRecord],
    *,
    repository_root: Path,
    verify_references: bool = True,
) -> None:
    session_ids = {record.session_id for record in records}
    finding_ids = [finding.finding_id for finding in findings]
    if len(finding_ids) != len(set(finding_ids)):
        raise ValueError("Usability finding_id values must be unique.")
    for index, finding in enumerate(findings, 2):
        _validate_finding(finding, row_number=index)
        unknown_sessions = set(finding.affected_session_ids) - session_ids
        if unknown_sessions:
            raise ValueError(
                f"Finding row {index} references unknown session IDs: "
                + ", ".join(sorted(unknown_sessions))
            )
        if verify_references:
            _verify_finding_reference(
                finding, row_number=index, repository_root=repository_root
            )


def _validate_record(record: UsabilityRecord, *, row_number: int) -> None:
    if SESSION_ID_PATTERN.fullmatch(record.session_id) is None:
        raise ValueError(f"Row {row_number} session_id must use study-local form U01-U999.")
    if record.scenario_id not in SCENARIO_IDS:
        raise ValueError(f"Row {row_number} has an unsupported scenario_id.")
    if record.participant_type not in PARTICIPANT_TYPES:
        raise ValueError(f"Row {row_number} has an unsupported participant_type.")
    if not 0 <= record.completion_seconds <= 3600:
        raise ValueError(f"Row {row_number} completion_seconds must be between 0 and 3600.")
    if (
        not SCENARIO_LIMITATION_REQUIREMENTS[record.scenario_id]
        and record.limitation_visible
    ):
        raise ValueError(
            f"Row {row_number} limitation_visible cannot be true for this scenario."
        )


def _validate_finding(finding: UsabilityFinding, *, row_number: int) -> None:
    if FINDING_ID_PATTERN.fullmatch(finding.finding_id) is None:
        raise ValueError(f"Finding row {row_number} finding_id must use form F01-F999.")
    if finding.issue_tag not in ISSUE_TAGS:
        raise ValueError(f"Finding row {row_number} has an unsupported issue_tag.")
    if finding.severity not in ISSUE_SEVERITIES:
        raise ValueError(f"Finding row {row_number} has an unsupported severity.")
    if finding.status not in ISSUE_STATUSES:
        raise ValueError(f"Finding row {row_number} has an unsupported status.")
    if not finding.affected_session_ids:
        raise ValueError(f"Finding row {row_number} needs affected_session_ids.")
    if any(
        SESSION_ID_PATTERN.fullmatch(session_id) is None
        for session_id in finding.affected_session_ids
    ):
        raise ValueError(f"Finding row {row_number} has an invalid affected session ID.")
    if (finding.severity == "critical") != finding.critical:
        raise ValueError(
            f"Finding row {row_number} critical and severity must agree."
        )
    if finding.critical and not finding.reference:
        raise ValueError(f"Finding row {row_number} critical issue needs a reference.")
    expected_pattern = {
        "open": OPEN_REFERENCE_PATTERN,
        "documented": DOCUMENT_REFERENCE_PATTERN,
        "resolved": COMMIT_REFERENCE_PATTERN,
    }[finding.status]
    if finding.reference and expected_pattern.fullmatch(finding.reference) is None:
        raise ValueError(
            f"Finding row {row_number} reference does not prove its {finding.status} status."
        )
    if finding.status != "open" and not finding.reference:
        raise ValueError(
            f"Finding row {row_number} needs a reference for {finding.status} status."
        )


def _verify_finding_reference(
    finding: UsabilityFinding, *, row_number: int, repository_root: Path
) -> None:
    if finding.status == "documented":
        relative_path = finding.reference.removeprefix("docs:")
        reference_path = (repository_root / relative_path).resolve()
        try:
            reference_path.relative_to(repository_root.resolve())
        except ValueError as error:
            raise ValueError(
                f"Finding row {row_number} documentation reference escapes the repository."
            ) from error
        if not reference_path.is_file():
            raise ValueError(
                f"Finding row {row_number} documentation reference does not exist."
            )
    elif finding.status == "resolved":
        revision = finding.reference.removeprefix("commit:")
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
            cwd=repository_root,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise ValueError(
                f"Finding row {row_number} resolved commit does not exist."
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


def _issue_tag_counts(findings: Sequence[UsabilityFinding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.issue_tag] = (
            counts.get(finding.issue_tag, 0) + len(finding.affected_session_ids)
        )
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _prioritized_issues(
    findings: Sequence[UsabilityFinding],
) -> list[dict[str, Any]]:
    aggregates: dict[str, dict[str, Any]] = {}
    for finding in findings:
        issue = aggregates.setdefault(
            finding.issue_tag,
            {
                "tag": finding.issue_tag,
                "affected_session_ids": set(),
                "blocked_findings": 0,
                "critical_findings": 0,
                "unresolved_critical_findings": 0,
                "highest_severity": "low",
                "open_findings": 0,
                "documented_findings": 0,
                "resolved_findings": 0,
            },
        )
        issue["affected_session_ids"].update(finding.affected_session_ids)
        issue["blocked_findings"] += int(finding.task_blocked)
        issue["critical_findings"] += int(finding.critical)
        issue["unresolved_critical_findings"] += int(
            finding.critical and finding.status == "open"
        )
        issue[f"{finding.status}_findings"] += 1
        if SEVERITY_WEIGHTS[finding.severity] > SEVERITY_WEIGHTS[issue["highest_severity"]]:
            issue["highest_severity"] = finding.severity
    prioritized = []
    for issue in aggregates.values():
        issue["affected_sessions"] = len(issue.pop("affected_session_ids"))
        issue["priority_score"] = (
            SEVERITY_WEIGHTS[issue["highest_severity"]] * 100
            + issue["unresolved_critical_findings"] * 50
            + issue["blocked_findings"] * 20
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
