from datetime import date

import mcgill_care_compass.maintenance as maintenance_module
from mcgill_care_compass.maintenance import (
    build_maintenance_report,
    format_maintenance_markdown,
)


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

    report = build_maintenance_report(pages, links, [], as_of=date(2026, 7, 19))

    assert report["failed_sources"]["count"] == 1
    assert report["failed_sources"]["records"][0]["canonical_url"].endswith("/missing")
    assert report["intentional_link_skips"]["count"] == 1
    assert report["intentional_link_skips"]["by_reason"] == {"duplicate_url": 1}


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
