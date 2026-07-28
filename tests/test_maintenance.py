from datetime import date

import mcgill_care_compass.maintenance as maintenance_module
from mcgill_care_compass.maintenance import (
    build_maintenance_report,
    format_maintenance_markdown,
)

REVIEWED_NONBLOCKING = {
    "disposition": "reviewed_nonblocking",
    "reason": "Discovered page is not required for current category coverage.",
    "reviewed_at": "2026-07-19",
    "review_reference": "Issue #11",
    "pipeline_run_id": "test-run",
}


def _isolate_failed_source_findings(monkeypatch) -> None:
    monkeypatch.setattr(
        maintenance_module,
        "_missing_report",
        lambda *args: {"rows_with_missing_data": 0, "missing_by_field": {}, "examples": []},
    )
    monkeypatch.setattr(
        maintenance_module,
        "_coverage_report",
        lambda *args: {
            "by_category": {},
            "categories_without_pages": [],
            "categories_without_chunks": [],
        },
    )
    monkeypatch.setattr(maintenance_module, "_chunk_quality_report", lambda *args, **kwargs: {})


def test_maintenance_separates_failed_fetches_from_intentional_link_skips() -> None:
    pages = [
        {
            "canonical_url": "https://www.mcgill.ca/good",
            "http_status": "200",
            "drift_status": "unchanged",
            "retrieved_at": "2026-07-18T00:00:00+00:00",
        },
        {
            "canonical_url": "https://www.mcgill.ca/missing",
            "http_status": "404",
            "drift_status": "fetch_failed",
            "retrieved_at": "2026-06-01T00:00:00+00:00",
            "fetch_error": "HTTP 404",
            "pipeline_run_id": "test-run",
        },
    ]
    links = [
        {
            "source_canonical_url": "https://www.mcgill.ca/good",
            "target_canonical_url": "https://www.mcgill.ca/duplicate",
            "link_type": "in_scope",
            "crawl_decision": "not_crawled",
            "skip_reason": "duplicate_url",
        }
    ]

    report = build_maintenance_report(
        pages,
        links,
        [],
        failed_source_dispositions={
            "https://www.mcgill.ca/missing": REVIEWED_NONBLOCKING
        },
        as_of=date(2026, 7, 19),
    )

    assert report["report_schema_version"] == "2"
    assert report["failed_sources"]["count"] == 1
    assert report["failed_sources"]["blocking_count"] == 0
    assert report["failed_sources"]["nonblocking_count"] == 1
    assert report["failed_sources"]["records"][0]["canonical_url"].endswith("/missing")
    assert report["failed_sources"]["records"][0]["active_chunk_count"] == 0
    assert (
        report["failed_sources"]["records"][0]["classification"]
        == "reviewed_nonblocking"
    )
    assert report["intentional_link_skips"]["count"] == 1
    assert report["intentional_link_skips"]["by_reason"] == {"duplicate_url": 1}


def test_failed_source_blocks_once_without_reviewed_disposition(monkeypatch) -> None:
    _isolate_failed_source_findings(monkeypatch)
    failed_page = {
        "canonical_url": "https://www.mcgill.ca/unavailable",
        "http_status": "404",
        "drift_status": "fetch_failed",
        "retrieved_at": "2026-07-18T00:00:00+00:00",
        "fetch_error": "HTTP 404",
        "pipeline_run_id": "test-run",
    }

    undisposed_report = build_maintenance_report(
        [failed_page],
        [],
        [],
        as_of=date(2026, 7, 19),
    )
    reviewed_report = build_maintenance_report(
        [failed_page],
        [],
        [],
        failed_source_dispositions={
            failed_page["canonical_url"]: REVIEWED_NONBLOCKING
        },
        as_of=date(2026, 7, 19),
    )
    exposed_report = build_maintenance_report(
        [failed_page],
        [],
        [
            {
                "chunk_id": "stale-source-chunk",
                "canonical_url": failed_page["canonical_url"],
                "chunk_text": "An active chunk from an unavailable source.",
            }
        ],
        failed_source_dispositions={
            failed_page["canonical_url"]: REVIEWED_NONBLOCKING
        },
        as_of=date(2026, 7, 19),
    )

    assert undisposed_report["has_errors"] is True
    assert undisposed_report["severity_counts"] == {"error": 1, "warning": 0, "info": 0}
    assert undisposed_report["failed_sources"]["blocking_count"] == 1
    assert reviewed_report["has_errors"] is False
    assert reviewed_report["severity_counts"] == {"error": 0, "warning": 1, "info": 0}
    assert reviewed_report["failed_sources"]["nonblocking_count"] == 1
    assert exposed_report["has_errors"] is True
    assert exposed_report["severity_counts"]["error"] == 1
    assert exposed_report["failed_sources"]["blocking_count"] == 1


def test_incomplete_failed_source_disposition_does_not_bypass_gate(monkeypatch) -> None:
    _isolate_failed_source_findings(monkeypatch)
    failed_url = "https://www.mcgill.ca/unavailable"

    report = build_maintenance_report(
        [
            {
                "canonical_url": failed_url,
                "http_status": "404",
                "drift_status": "fetch_failed",
                "fetch_error": "HTTP 404",
                "pipeline_run_id": "test-run",
            }
        ],
        [],
        [],
        failed_source_dispositions={
            failed_url: {
                "disposition": "reviewed_nonblocking",
                "reason": "",
                "reviewed_at": "2026-07-19",
                "review_reference": "Issue #11",
                "pipeline_run_id": "test-run",
            }
        },
        as_of=date(2026, 7, 19),
    )

    assert report["has_errors"] is True
    assert report["failed_sources"]["records"][0]["classification"] == "blocking"


def test_disposition_for_previous_pipeline_run_does_not_bypass_gate(monkeypatch) -> None:
    _isolate_failed_source_findings(monkeypatch)
    failed_url = "https://www.mcgill.ca/unavailable"
    old_disposition = REVIEWED_NONBLOCKING | {"pipeline_run_id": "previous-run"}

    report = build_maintenance_report(
        [
            {
                "canonical_url": failed_url,
                "http_status": "404",
                "drift_status": "fetch_failed",
                "fetch_error": "HTTP 404",
                "pipeline_run_id": "current-run",
            }
        ],
        [],
        [],
        failed_source_dispositions={failed_url: old_disposition},
        as_of=date(2026, 7, 19),
    )

    assert report["has_errors"] is True
    assert report["failed_sources"]["records"][0]["classification"] == "blocking"


def test_maintenance_classifies_chunk_quality_and_category_coverage() -> None:
    chunks = [
        {
            "chunk_id": "short",
            "chunk_text": "Quick Links",
            "category_id": "housing",
            "nearby_links": "[]",
        },
        {
            "chunk_id": "duplicate-a",
            "chunk_text": "Same useful text for students to review with official staff.",
            "category_id": "housing",
            "has_contact_info": "true",
        },
        {
            "chunk_id": "duplicate-b",
            "chunk_text": "Same useful text for students to review with official staff!",
            "category_id": "housing",
            "has_contact_info": "true",
        },
    ]

    report = build_maintenance_report([], [], chunks, as_of=date(2026, 7, 19))

    assert report["chunk_quality"]["very_short_non_actionable"]["count"] == 1
    assert report["chunk_quality"]["boilerplate_pattern"]["count"] == 1
    assert report["chunk_quality"]["duplicate_normalized_text"]["count"] == 2
    assert report["category_coverage"]["by_category"]["housing"]["chunks"] == 3
    assert report["chunk_quality"]["boilerplate_pattern"]["examples"] == [
        {"chunk_id": "short", "canonical_url": ""}
    ]


def test_maintenance_markdown_contains_actionable_examples() -> None:
    report = build_maintenance_report(
        [
            {
                "canonical_url": "https://www.mcgill.ca/changed",
                "drift_status": "changed",
                "retrieved_at": "2026-07-18T00:00:00+00:00",
                "source_updated_at": "",
            }
        ],
        [
            {
                "target_canonical_url": "https://www.mcgill.ca/duplicate",
                "crawl_decision": "not_crawled",
                "skip_reason": "duplicate_url",
            }
        ],
        [
            {
                "chunk_id": "short",
                "canonical_url": "https://www.mcgill.ca/changed",
                "chunk_text": "Quick Links",
                "category_id": "housing",
            }
        ],
        as_of=date(2026, 7, 19),
    )

    markdown = format_maintenance_markdown(report)

    assert "### Changed examples" in markdown
    assert "https://www.mcgill.ca/changed" in markdown
    assert "duplicate_url: 1" in markdown
    assert "chunk_id=short" in markdown


def test_changed_or_new_sources_require_attention_even_without_other_findings(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        maintenance_module,
        "_missing_report",
        lambda *args: {"rows_with_missing_data": 0, "missing_by_field": {}, "examples": []},
    )
    monkeypatch.setattr(
        maintenance_module,
        "_coverage_report",
        lambda *args: {"by_category": {}, "categories_without_chunks": []},
    )
    monkeypatch.setattr(maintenance_module, "_chunk_quality_report", lambda *args, **kwargs: {})

    report = build_maintenance_report(
        [
            {
                "canonical_url": "https://www.mcgill.ca/changed",
                "http_status": "200",
                "drift_status": "changed",
                "retrieved_at": "2026-07-19T00:00:00+00:00",
            }
        ],
        [],
        [],
        as_of=date(2026, 7, 19),
    )

    assert report["requires_attention"] is True
