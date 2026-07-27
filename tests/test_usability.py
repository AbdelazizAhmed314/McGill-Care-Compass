import csv

import pytest

from mcgill_care_compass.usability import (
    REQUIRED_FIELDS,
    analyze_usability,
    load_usability_records,
)


def write_records(path, rows) -> None:  # noqa: ANN001
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def passing_row(index: int) -> dict[str, str]:
    return {
        "session_id": f"U{index:02d}",
        "participant_type": "target" if index < 5 else "proxy",
        "scenario_id": f"UT{index:02d}",
        "completed": "true",
        "completion_seconds": "90",
        "identified_next_step": "true",
        "relevant_service_top_three": "true",
        "explanation_understood": "true",
        "source_link_visible": "true",
        "limitation_visible": "true",
        "confidence_before": "2",
        "confidence_after": "4",
        "usefulness_rating": "5",
        "critical_issue": "false",
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
    assert report["privacy"]["contains_participant_identifiers"] is False


def test_analyze_usability_requires_five_records_and_no_critical_issue(tmp_path) -> None:
    path = tmp_path / "records.csv"
    rows = [passing_row(index) for index in range(1, 5)]
    rows[0]["critical_issue"] = "true"
    write_records(path, rows)

    report = analyze_usability(load_usability_records(path))

    assert report["status"] == "needs_attention"
    assert not report["targets"]["minimum_records"]
    assert not report["targets"]["no_unresolved_critical_issues"]


def test_loader_rejects_unapproved_identity_field(tmp_path) -> None:
    path = tmp_path / "records.csv"
    headers = [*REQUIRED_FIELDS, "participant_email"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerow({**passing_row(1), "participant_email": "not-allowed@example.com"})

    with pytest.raises(ValueError, match="unexpected: participant_email"):
        load_usability_records(path)


def test_loader_rejects_duplicate_session_ids(tmp_path) -> None:
    path = tmp_path / "records.csv"
    row = passing_row(1)
    write_records(path, [row, row])

    with pytest.raises(ValueError, match="must be unique"):
        load_usability_records(path)
