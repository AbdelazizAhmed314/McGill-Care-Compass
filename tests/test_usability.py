import csv

import pytest

from mcgill_care_compass.usability import (
    FINDING_FIELDS,
    REQUIRED_FIELDS,
    analyze_usability,
    load_proxy_justification,
    load_usability_findings,
    load_usability_records,
    verify_usability_reports,
    write_usability_reports,
)

SCENARIOS = (
    "UT01_INSURANCE",
    "UT02_HEALTHCARE",
    "UT03_HOUSING",
    "UT04_DOCUMENTS",
    "UT05_TAX",
)


def write_csv(path, fields, rows) -> None:  # noqa: ANN001
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def passing_row(index: int) -> dict[str, str]:
    scenario_id = SCENARIOS[(index - 1) % len(SCENARIOS)]
    return {
        "session_id": f"U{index:02d}",
        "participant_type": "target" if index < 5 else "proxy",
        "scenario_id": scenario_id,
        "completed": "true",
        "completion_seconds": "90",
        "identified_next_step": "true",
        "relevant_service_top_three": "true",
        "explanation_understood": "true",
        "source_link_visible": "true",
        "limitation_visible": str(scenario_id != "UT04_DOCUMENTS").lower(),
        "confidence_before": "2",
        "confidence_after": "4",
        "usefulness_rating": "5",
    }


def finding_row(
    *,
    finding_id: str = "F01",
    tag: str = "wording",
    severity: str = "low",
    blocked: bool = False,
    critical: bool = False,
    status: str = "open",
    reference: str = "",
    sessions: str = "U01",
) -> dict[str, str]:
    return {
        "finding_id": finding_id,
        "issue_tag": tag,
        "severity": severity,
        "task_blocked": str(blocked).lower(),
        "critical": str(critical).lower(),
        "status": status,
        "reference": reference,
        "affected_session_ids": sessions,
    }


def load_sample(tmp_path, rows=None, findings=None):  # noqa: ANN001
    records_path = tmp_path / "records.csv"
    findings_path = tmp_path / "findings.csv"
    write_csv(
        records_path,
        REQUIRED_FIELDS,
        rows or [passing_row(index) for index in range(1, 6)],
    )
    write_csv(findings_path, FINDING_FIELDS, findings or [])
    records = load_usability_records(records_path)
    loaded_findings = load_usability_findings(
        findings_path, records, repository_root=tmp_path
    )
    return records, loaded_findings


def test_analyze_usability_passes_complete_anonymous_sample(tmp_path) -> None:
    records, findings = load_sample(
        tmp_path, findings=[finding_row()]
    )

    report = analyze_usability(records, findings)

    assert report["status"] == "ready"
    assert report["metrics"]["completed_records"] == 5
    assert report["metrics"]["median_completion_seconds"] == 90
    assert report["metrics"]["average_confidence_change"] == 2
    assert report["scenario_counts"] == {scenario: 1 for scenario in SCENARIOS}
    assert report["issue_tag_counts"] == {"wording": 1}
    assert report["prioritized_issues"][0]["highest_severity"] == "low"
    assert report["privacy"]["direct_identifiers_rejected"] is True


def test_analyze_usability_counts_only_completed_records(tmp_path) -> None:
    rows = [passing_row(index) for index in range(1, 6)]
    for row in rows[1:]:
        row["completed"] = "false"
    records, findings = load_sample(tmp_path, rows=rows)

    report = analyze_usability(records, findings)

    assert report["status"] == "needs_attention"
    assert report["metrics"]["completed_records"] == 1
    assert report["metrics"]["task_completion_rate"] == 0.2
    assert not report["targets"]["minimum_completed_records"]
    assert not report["targets"]["task_completion"]


def test_analyze_usability_requires_all_five_scenarios(tmp_path) -> None:
    rows = [passing_row(index) for index in range(1, 6)]
    for row in rows:
        row["scenario_id"] = "UT01_INSURANCE"
        row["limitation_visible"] = "true"
    records, findings = load_sample(tmp_path, rows=rows)

    report = analyze_usability(records, findings)

    assert report["metrics"]["completed_records"] == 5
    assert not report["targets"]["scenario_coverage"]
    assert report["status"] == "needs_attention"


def test_analyze_usability_requires_verified_critical_issue_disposition(
    tmp_path,
) -> None:
    open_finding = finding_row(
        severity="critical",
        critical=True,
        status="open",
        reference="issue:#10",
    )
    records, findings = load_sample(tmp_path, findings=[open_finding])

    report = analyze_usability(records, findings)

    assert report["status"] == "needs_attention"
    assert report["metrics"]["unresolved_critical_issue_count"] == 1

    evidence = tmp_path / "docs" / "usability" / "f01.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("# F01 disposition\n", encoding="utf-8")
    documented = {
        **open_finding,
        "status": "documented",
        "reference": "docs:docs/usability/f01.md",
    }
    records, findings = load_sample(tmp_path, findings=[documented])

    assert analyze_usability(records, findings)["status"] == "ready"


def test_finding_status_cannot_rely_on_unverifiable_reference(tmp_path) -> None:
    records_path = tmp_path / "records.csv"
    findings_path = tmp_path / "findings.csv"
    write_csv(
        records_path,
        REQUIRED_FIELDS,
        [passing_row(index) for index in range(1, 6)],
    )
    records = load_usability_records(records_path)
    write_csv(
        findings_path,
        FINDING_FIELDS,
        [finding_row(status="documented", reference="docs:docs/missing.md")],
    )

    with pytest.raises(ValueError, match="does not exist"):
        load_usability_findings(findings_path, records, repository_root=tmp_path)


def test_all_proxy_sample_requires_privacy_safe_recruitment_justification(
    tmp_path,
) -> None:
    rows = [passing_row(index) for index in range(1, 6)]
    for row in rows:
        row["participant_type"] = "proxy"
    records, findings = load_sample(tmp_path, rows=rows)

    report = analyze_usability(records, findings)

    assert report["recruitment"]["all_proxy_sample"] is True
    assert not report["targets"]["target_or_justified_proxy_sample"]

    justification = tmp_path / "proxy.md"
    justification.write_text(
        "Target-cohort recruitment was attempted, but scheduling was unavailable; "
        "five proxy users were therefore used under the approved fallback.",
        encoding="utf-8",
    )
    justification_sha = load_proxy_justification(justification)
    justified_report = analyze_usability(
        records, findings, proxy_justification_sha256=justification_sha
    )

    assert justified_report["status"] == "ready"
    assert justified_report["recruitment"]["proxy_justification_sha256"]


def test_prioritized_issues_keep_finding_level_severity_and_status(tmp_path) -> None:
    findings_rows = [
        finding_row(),
        finding_row(
            finding_id="F02",
            tag="ranking",
            severity="high",
            blocked=True,
            sessions="U02|U03",
        ),
        finding_row(
            finding_id="F03",
            tag="safety",
            severity="critical",
            critical=True,
            reference="issue:#99",
            sessions="U04",
        ),
    ]
    records, findings = load_sample(tmp_path, findings=findings_rows)

    report = analyze_usability(records, findings)

    assert [issue["tag"] for issue in report["prioritized_issues"]] == [
        "safety",
        "ranking",
        "wording",
    ]
    assert report["prioritized_issues"][0]["unresolved_critical_findings"] == 1
    assert report["prioritized_issues"][1]["affected_sessions"] == 2


def test_loader_rejects_unapproved_identity_field(tmp_path) -> None:
    path = tmp_path / "records.csv"
    write_csv(
        path,
        (*REQUIRED_FIELDS, "participant_email"),
        [{**passing_row(1), "participant_email": "not-allowed@example.com"}],
    )

    with pytest.raises(ValueError, match="unexpected: participant_email"):
        load_usability_records(path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("session_id", "person@example.com", "study-local form"),
        ("scenario_id", "UT99_CUSTOM", "unsupported scenario_id"),
        ("limitation_visible", "false", None),
    ],
)
def test_loader_rejects_identifying_or_uncontrolled_values(
    tmp_path, field, value, message  # noqa: ANN001
) -> None:
    path = tmp_path / "records.csv"
    row = passing_row(1)
    row[field] = value
    write_csv(path, REQUIRED_FIELDS, [row])

    if message is None:
        assert load_usability_records(path)
    else:
        with pytest.raises(ValueError, match=message):
            load_usability_records(path)


def test_non_limitation_scenario_cannot_claim_limitation_visibility(tmp_path) -> None:
    path = tmp_path / "records.csv"
    row = passing_row(4)
    row["limitation_visible"] = "true"
    write_csv(path, REQUIRED_FIELDS, [row])

    with pytest.raises(ValueError, match="cannot be true"):
        load_usability_records(path)


def test_finding_cannot_reference_unknown_session(tmp_path) -> None:
    records_path = tmp_path / "records.csv"
    findings_path = tmp_path / "findings.csv"
    write_csv(records_path, REQUIRED_FIELDS, [passing_row(1)])
    write_csv(
        findings_path,
        FINDING_FIELDS,
        [finding_row(sessions="U99")],
    )

    records = load_usability_records(records_path)
    with pytest.raises(ValueError, match="unknown session"):
        load_usability_findings(findings_path, records, repository_root=tmp_path)


def test_report_verification_detects_drift(tmp_path) -> None:
    records, findings = load_sample(tmp_path)
    report = analyze_usability(records, findings)
    json_path = tmp_path / "findings.json"
    markdown_path = tmp_path / "findings.md"
    write_usability_reports(report, json_path=json_path, markdown_path=markdown_path)

    verify_usability_reports(
        report, json_path=json_path, markdown_path=markdown_path
    )
    markdown_path.write_text("stale\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Markdown"):
        verify_usability_reports(
            report, json_path=json_path, markdown_path=markdown_path
        )
