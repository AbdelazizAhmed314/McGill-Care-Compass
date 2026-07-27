import csv

import pytest

from mcgill_care_compass.usability import (
    REQUIRED_FIELDS,
    analyze_usability,
    load_usability_records,
)

SCENARIOS = (
    "UT01_INSURANCE",
    "UT02_HEALTHCARE",
    "UT03_HOUSING",
    "UT04_DOCUMENTS",
    "UT05_TAX",
)


def write_records(path, rows) -> None:  # noqa: ANN001
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def passing_row(index: int) -> dict[str, str]:
    scenario_id = SCENARIOS[(index - 1) % len(SCENARIOS)]
    limitation_required = scenario_id != "UT04_DOCUMENTS"
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
        "limitation_required": str(limitation_required).lower(),
        "limitation_visible": str(limitation_required).lower(),
        "confidence_before": "2",
        "confidence_after": "4",
        "usefulness_rating": "5",
        "critical_issue": "false",
        "issue_severity": "low" if index == 1 else "none",
        "task_blocked": "false",
        "issue_status": "open" if index == 1 else "none",
        "issue_reference": "",
        "issue_tags": "wording" if index == 1 else "",
    }


def test_analyze_usability_passes_complete_anonymous_sample(tmp_path) -> None:
    path = tmp_path / "records.csv"
    write_records(path, [passing_row(index) for index in range(1, 6)])

    report = analyze_usability(load_usability_records(path))

    assert report["status"] == "ready"
    assert report["metrics"]["completed_records"] == 5
    assert report["metrics"]["median_completion_seconds"] == 90
    assert report["metrics"]["average_confidence_change"] == 2
    assert report["issue_tag_counts"] == {"wording": 1}
    assert report["prioritized_issues"][0]["highest_severity"] == "low"
    assert report["privacy"]["validated_record_contract"] is True
    assert report["privacy"]["contains_participant_identifiers"] is False


def test_analyze_usability_counts_only_completed_records(tmp_path) -> None:
    path = tmp_path / "records.csv"
    rows = [passing_row(index) for index in range(1, 6)]
    for row in rows[1:]:
        row["completed"] = "false"
    write_records(path, rows)

    report = analyze_usability(load_usability_records(path))

    assert report["status"] == "needs_attention"
    assert report["metrics"]["record_count"] == 5
    assert report["metrics"]["completed_records"] == 1
    assert report["metrics"]["task_completion_rate"] == 0.2
    assert not report["targets"]["minimum_completed_records"]
    assert not report["targets"]["task_completion"]


def test_analyze_usability_requires_critical_issue_resolution(tmp_path) -> None:
    path = tmp_path / "records.csv"
    rows = [passing_row(index) for index in range(1, 6)]
    rows[0].update(
        {
            "critical_issue": "true",
            "issue_severity": "critical",
            "issue_status": "open",
            "issue_reference": "issue:#10",
            "issue_tags": "safety",
        }
    )
    write_records(path, rows)

    report = analyze_usability(load_usability_records(path))

    assert report["status"] == "needs_attention"
    assert report["metrics"]["unresolved_critical_issue_count"] == 1
    assert not report["targets"]["no_unresolved_critical_issues"]

    rows[0]["issue_status"] = "documented"
    write_records(path, rows)
    documented_report = analyze_usability(load_usability_records(path))

    assert documented_report["status"] == "ready"
    assert documented_report["metrics"]["critical_issue_count"] == 1
    assert documented_report["metrics"]["unresolved_critical_issue_count"] == 0


def test_source_and_required_limitation_visibility_are_acceptance_targets(tmp_path) -> None:
    path = tmp_path / "records.csv"
    rows = [passing_row(index) for index in range(1, 6)]
    for row in rows:
        row["source_link_visible"] = "false"
        row["limitation_visible"] = "false"
    write_records(path, rows)

    report = analyze_usability(load_usability_records(path))

    assert report["status"] == "needs_attention"
    assert not report["targets"]["source_link_visible"]
    assert not report["targets"]["limitation_visible"]


def test_all_proxy_sample_is_reported_without_overriding_issue_10_gate(tmp_path) -> None:
    path = tmp_path / "records.csv"
    rows = [passing_row(index) for index in range(1, 6)]
    for row in rows:
        row["participant_type"] = "proxy"
    write_records(path, rows)

    report = analyze_usability(load_usability_records(path))

    assert report["status"] == "ready"
    assert report["recruitment"]["all_proxy_sample"] is True
    assert report["recruitment"]["target_participant_preferred"] is False


def test_prioritized_issues_use_safety_severity_blocking_and_frequency(tmp_path) -> None:
    path = tmp_path / "records.csv"
    rows = [passing_row(index) for index in range(1, 6)]
    rows[1].update(
        {
            "issue_tags": "ranking",
            "issue_severity": "high",
            "task_blocked": "true",
            "issue_status": "open",
        }
    )
    rows[2].update(
        {
            "issue_tags": "safety",
            "issue_severity": "critical",
            "critical_issue": "true",
            "issue_status": "open",
            "issue_reference": "issue:#99",
        }
    )
    write_records(path, rows)

    report = analyze_usability(load_usability_records(path))

    assert [issue["tag"] for issue in report["prioritized_issues"]] == [
        "safety",
        "ranking",
        "wording",
    ]
    assert report["prioritized_issues"][0]["unresolved_critical_sessions"] == 1
    assert report["prioritized_issues"][1]["blocked_sessions"] == 1


def test_loader_rejects_unapproved_identity_field(tmp_path) -> None:
    path = tmp_path / "records.csv"
    headers = [*REQUIRED_FIELDS, "participant_email"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerow({**passing_row(1), "participant_email": "not-allowed@example.com"})

    with pytest.raises(ValueError, match="unexpected: participant_email"):
        load_usability_records(path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("session_id", "person@example.com", "study-local form"),
        ("scenario_id", "UT99_CUSTOM", "unsupported scenario_id"),
        ("issue_tags", "Jane Doe shared a visa number", "unsupported issue_tags"),
        ("issue_reference", "person@example.com", "unsupported issue_reference"),
        ("limitation_required", "false", "does not match the scenario contract"),
    ],
)
def test_loader_rejects_identifying_or_uncontrolled_values(
    tmp_path, field, value, message  # noqa: ANN001
) -> None:
    path = tmp_path / "records.csv"
    row = passing_row(1)
    row[field] = value
    write_records(path, [row])

    with pytest.raises(ValueError, match=message):
        load_usability_records(path)


def test_loader_rejects_duplicate_session_ids(tmp_path) -> None:
    path = tmp_path / "records.csv"
    row = passing_row(1)
    write_records(path, [row, row])

    with pytest.raises(ValueError, match="must be unique"):
        load_usability_records(path)
