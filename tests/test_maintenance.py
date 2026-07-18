from pathlib import Path

import pandas as pd

from mcgill_care_compass.maintenance import (
    MaintenanceReportPaths,
    build_maintenance_report,
    write_maintenance_report,
)


def test_build_maintenance_report_summarizes_outputs(tmp_path: Path) -> None:
    pages = pd.DataFrame(
        [
            {
                "canonical_url": "https://example.test/ok",
                "http_status": "200",
                "retrieved_at": "2026-07-01T00:00:00+00:00",
                "source_updated_at": "",
                "freshness_score": "0.4",
                "drift_status": "changed",
                "fetch_error": "",
                "category_id": "insurance",
            },
            {
                "canonical_url": "https://example.test/fail",
                "http_status": "404",
                "retrieved_at": "2026-07-02T00:00:00+00:00",
                "source_updated_at": "2026-06-01",
                "freshness_score": "0.8",
                "drift_status": "fetch_failed",
                "fetch_error": "not found",
                "category_id": "tax",
            },
        ]
    )
    links = pd.DataFrame(
        [
            {
                "source_canonical_url": "https://example.test/ok",
                "target_canonical_url": "https://example.test/fail",
                "link_type": "in_scope",
                "crawl_decision": "not_crawled",
                "skip_reason": "depth_limit",
            }
        ]
    )
    chunks = pd.DataFrame(
        [
            {
                "chunk_id": "chunk-1",
                "canonical_url": "https://example.test/ok",
                "category_id": "insurance",
                "chunk_text": "Use the official source.",
                "retrieved_at": "2026-07-01T00:00:00+00:00",
                "source_updated_at": "",
                "review_status": "silver_unreviewed",
                "label_confidence": "high",
                "freshness_score": "0.4",
            }
        ]
    )
    pages_csv = tmp_path / "pages.csv"
    links_csv = tmp_path / "links.csv"
    chunks_csv = tmp_path / "chunks.csv"
    pages.to_csv(pages_csv, index=False)
    links.to_csv(links_csv, index=False)
    chunks.to_csv(chunks_csv, index=False)

    report = build_maintenance_report(
        MaintenanceReportPaths(
            pages_csv=pages_csv,
            links_csv=links_csv,
            chunks_csv=chunks_csv,
            markdown_report=tmp_path / "report.md",
            json_report=tmp_path / "report.json",
        )
    )

    assert report["broken_links"]["non_200_pages"] == 1
    assert report["broken_links"]["not_crawled_links"] == 1
    assert report["source_freshness"]["chunks_low_freshness_score"] == 1
    assert "tax" in report["category_coverage"]["observed_categories"]


def test_write_maintenance_report_creates_markdown_and_json(tmp_path: Path) -> None:
    pages_csv = tmp_path / "pages.csv"
    links_csv = tmp_path / "links.csv"
    chunks_csv = tmp_path / "chunks.csv"
    pd.DataFrame([{
        "canonical_url": "u",
        "category_id": "insurance",
    }]).to_csv(pages_csv, index=False)
    pd.DataFrame([{"source_canonical_url": "u", "target_canonical_url": "v"}]).to_csv(
        links_csv,
        index=False,
    )
    pd.DataFrame([{"chunk_id": "c", "category_id": "insurance"}]).to_csv(chunks_csv, index=False)
    markdown = tmp_path / "maintenance.md"
    json_report = tmp_path / "maintenance.json"

    write_maintenance_report(
        MaintenanceReportPaths(
            pages_csv=pages_csv,
            links_csv=links_csv,
            chunks_csv=chunks_csv,
            markdown_report=markdown,
            json_report=json_report,
        )
    )

    assert markdown.exists()
    assert json_report.exists()
    assert "Category Coverage Output" in markdown.read_text(encoding="utf-8")
