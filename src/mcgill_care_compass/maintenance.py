"""Maintenance reporting for committed Silver RAG artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from mcgill_care_compass.retrieval import CATEGORY_LABELS

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
SILVER = DATA / "silver"
DATASETS = SILVER / "datasets"
REPORTS = SILVER / "reports"
PAGES_CSV = DATASETS / "rag_pages.csv"
LINKS_CSV = DATASETS / "rag_links.csv"
CHUNKS_CSV = DATASETS / "rag_chunks.csv"
DEFAULT_MD_REPORT = REPORTS / "maintenance_report.md"
DEFAULT_JSON_REPORT = REPORTS / "maintenance_report.json"

PAGE_REQUIRED = {
    "canonical_url",
    "http_status",
    "retrieved_at",
    "source_updated_at",
    "freshness_score",
    "drift_status",
    "fetch_error",
    "category_id",
}
LINK_REQUIRED = {
    "source_canonical_url",
    "target_canonical_url",
    "link_type",
    "crawl_decision",
    "skip_reason",
}
CHUNK_REQUIRED = {
    "chunk_id",
    "canonical_url",
    "category_id",
    "chunk_text",
    "retrieved_at",
    "source_updated_at",
    "review_status",
    "label_confidence",
    "freshness_score",
}
PAGE_VALUE_REQUIRED = PAGE_REQUIRED - {"fetch_error"}
LINK_VALUE_REQUIRED = LINK_REQUIRED - {"skip_reason"}
CHUNK_VALUE_REQUIRED = CHUNK_REQUIRED


@dataclass(frozen=True)
class MaintenanceReportPaths:
    """Input and output paths for maintenance reporting."""

    pages_csv: Path = PAGES_CSV
    links_csv: Path = LINKS_CSV
    chunks_csv: Path = CHUNKS_CSV
    markdown_report: Path = DEFAULT_MD_REPORT
    json_report: Path = DEFAULT_JSON_REPORT


def read_artifact(path: Path) -> pd.DataFrame:
    """Read a CSV artifact as strings, returning an empty frame when missing."""

    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("").astype(str)


def missing_columns(frame: pd.DataFrame, required: set[str]) -> list[str]:
    """Return required columns missing from a frame."""

    return sorted(required - set(frame.columns))


def missing_values(frame: pd.DataFrame, columns: set[str]) -> dict[str, int]:
    """Count blank values for columns present in a frame."""

    counts: dict[str, int] = {}
    for column in sorted(columns & set(frame.columns)):
        count = int(frame[column].astype(str).str.strip().eq("").sum())
        if count:
            counts[column] = count
    return counts


def _numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce")


def source_freshness_summary(pages: pd.DataFrame, chunks: pd.DataFrame) -> dict[str, Any]:
    """Summarize source freshness and drift signals."""

    freshness = _numeric_series(chunks, "freshness_score")
    pages_retrieved = pages.get("retrieved_at", pd.Series(dtype="object"))
    chunks_retrieved = chunks.get("retrieved_at", pd.Series(dtype="object"))
    return {
        "page_retrieved_at_min": str(pages_retrieved.min()) if not pages.empty else "",
        "page_retrieved_at_max": str(pages_retrieved.max()) if not pages.empty else "",
        "chunk_retrieved_at_min": str(chunks_retrieved.min()) if not chunks.empty else "",
        "chunk_retrieved_at_max": str(chunks_retrieved.max()) if not chunks.empty else "",
        "pages_missing_source_updated_at": int(
            pages.get("source_updated_at", pd.Series(dtype="object"))
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        ),
        "chunks_missing_source_updated_at": int(
            chunks.get("source_updated_at", pd.Series(dtype="object"))
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        ),
        "chunks_low_freshness_score": int((freshness < 0.5).sum()) if not freshness.empty else 0,
        "drift_status_counts": _value_counts(pages, "drift_status"),
    }


def broken_link_summary(pages: pd.DataFrame, links: pd.DataFrame) -> dict[str, Any]:
    """Summarize broken/fetch-failed page and link signals."""

    failed_pages = pd.DataFrame()
    if "http_status" in pages.columns:
        failed_pages = pages[~pages["http_status"].astype(str).eq("200")]
    fetch_failed = pd.DataFrame()
    if "drift_status" in pages.columns:
        fetch_failed = pages[pages["drift_status"].astype(str).eq("fetch_failed")]
    fetch_errors = pd.DataFrame()
    if "fetch_error" in pages.columns:
        fetch_errors = pages[pages["fetch_error"].astype(str).str.strip().ne("")]
    not_crawled = pd.DataFrame()
    if "crawl_decision" in links.columns:
        not_crawled = links[links["crawl_decision"].astype(str).eq("not_crawled")]

    return {
        "non_200_pages": int(len(failed_pages)),
        "fetch_failed_pages": int(len(fetch_failed)),
        "pages_with_fetch_error": int(len(fetch_errors)),
        "not_crawled_links": int(len(not_crawled)),
        "non_200_examples": _examples(failed_pages, "canonical_url"),
        "fetch_error_examples": _examples(fetch_errors, "canonical_url"),
        "skip_reason_counts": _value_counts(links, "skip_reason"),
        "link_type_counts": _value_counts(links, "link_type"),
    }


def missing_data_summary(
    pages: pd.DataFrame,
    links: pd.DataFrame,
    chunks: pd.DataFrame,
) -> dict[str, Any]:
    """Summarize missing columns and blank required values."""

    return {
        "missing_page_columns": missing_columns(pages, PAGE_REQUIRED),
        "missing_link_columns": missing_columns(links, LINK_REQUIRED),
        "missing_chunk_columns": missing_columns(chunks, CHUNK_REQUIRED),
        "blank_page_values": missing_values(pages, PAGE_VALUE_REQUIRED),
        "blank_link_values": missing_values(links, LINK_VALUE_REQUIRED),
        "blank_chunk_values": missing_values(chunks, CHUNK_VALUE_REQUIRED),
    }


def category_coverage_summary(pages: pd.DataFrame, chunks: pd.DataFrame) -> dict[str, Any]:
    """Summarize coverage across the locked taxonomy."""

    expected = set(CATEGORY_LABELS)
    page_counts = _value_counts(pages, "category_id")
    chunk_counts = _value_counts(chunks, "category_id")
    observed = set(page_counts) | set(chunk_counts)
    return {
        "expected_categories": sorted(expected),
        "observed_categories": sorted(observed),
        "missing_categories": sorted(expected - observed),
        "page_counts_by_category": page_counts,
        "chunk_counts_by_category": chunk_counts,
        "low_chunk_coverage_categories": sorted(
            category for category in expected if int(chunk_counts.get(category, 0)) < 10
        ),
    }


def build_maintenance_report(paths: MaintenanceReportPaths | None = None) -> dict[str, Any]:
    """Build the maintenance report data structure from committed artifacts."""

    if paths is None:
        paths = MaintenanceReportPaths()
    pages = read_artifact(paths.pages_csv)
    links = read_artifact(paths.links_csv)
    chunks = read_artifact(paths.chunks_csv)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "inputs": {
            "pages_csv": _relative(paths.pages_csv),
            "links_csv": _relative(paths.links_csv),
            "chunks_csv": _relative(paths.chunks_csv),
        },
        "counts": {
            "pages": int(len(pages)),
            "links": int(len(links)),
            "chunks": int(len(chunks)),
        },
        "source_freshness": source_freshness_summary(pages, chunks),
        "broken_links": broken_link_summary(pages, links),
        "missing_data": missing_data_summary(pages, links, chunks),
        "category_coverage": category_coverage_summary(pages, chunks),
    }


def write_maintenance_report(
    paths: MaintenanceReportPaths | None = None,
) -> dict[str, Any]:
    """Build and write Markdown and JSON maintenance reports."""

    if paths is None:
        paths = MaintenanceReportPaths()
    report = build_maintenance_report(paths)
    paths.markdown_report.parent.mkdir(parents=True, exist_ok=True)
    paths.markdown_report.write_text(format_markdown_report(report), encoding="utf-8")
    paths.json_report.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def format_markdown_report(report: dict[str, Any]) -> str:
    """Format a maintenance report as Markdown."""

    freshness = report["source_freshness"]
    broken = report["broken_links"]
    missing = report["missing_data"]
    coverage = report["category_coverage"]
    lines = [
        "# Maintenance Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Inputs",
        "",
        f"- Pages: `{report['inputs']['pages_csv']}`",
        f"- Links: `{report['inputs']['links_csv']}`",
        f"- Chunks: `{report['inputs']['chunks_csv']}`",
        "",
        "## Counts",
        "",
        f"- Pages: {report['counts']['pages']}",
        f"- Links: {report['counts']['links']}",
        f"- Chunks: {report['counts']['chunks']}",
        "",
        "## Source Freshness",
        "",
        (
            f"- Page retrieval window: `{freshness['page_retrieved_at_min']}` "
            f"to `{freshness['page_retrieved_at_max']}`"
        ),
        (
            f"- Chunk retrieval window: `{freshness['chunk_retrieved_at_min']}` "
            f"to `{freshness['chunk_retrieved_at_max']}`"
        ),
        f"- Pages missing source-updated date: {freshness['pages_missing_source_updated_at']}",
        f"- Chunks missing source-updated date: {freshness['chunks_missing_source_updated_at']}",
        f"- Chunks with freshness score below 0.5: {freshness['chunks_low_freshness_score']}",
        "",
        "Drift status counts:",
        _markdown_counts(freshness["drift_status_counts"]),
        "",
        "## Broken Link And Fetch Output",
        "",
        f"- Non-200 pages: {broken['non_200_pages']}",
        f"- Fetch-failed pages: {broken['fetch_failed_pages']}",
        f"- Pages with fetch errors: {broken['pages_with_fetch_error']}",
        f"- Not-crawled links: {broken['not_crawled_links']}",
        "",
        "Skip reason counts:",
        _markdown_counts(broken["skip_reason_counts"]),
        "",
        "## Missing Data Output",
        "",
        f"- Missing page columns: {missing['missing_page_columns'] or 'none'}",
        f"- Missing link columns: {missing['missing_link_columns'] or 'none'}",
        f"- Missing chunk columns: {missing['missing_chunk_columns'] or 'none'}",
        f"- Blank page values: {missing['blank_page_values'] or 'none'}",
        f"- Blank link values: {missing['blank_link_values'] or 'none'}",
        f"- Blank chunk values: {missing['blank_chunk_values'] or 'none'}",
        "",
        "## Category Coverage Output",
        "",
        f"- Observed categories: {len(coverage['observed_categories'])}",
        f"- Missing categories: {coverage['missing_categories'] or 'none'}",
        f"- Low chunk coverage categories: {coverage['low_chunk_coverage_categories'] or 'none'}",
        "",
        "Chunk counts by category:",
        _markdown_counts(coverage["chunk_counts_by_category"]),
        "",
    ]
    return "\n".join(lines)


def _value_counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in frame.columns or frame.empty:
        return {}
    counts = frame[column].astype(str).replace("", "<blank>").value_counts().sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def _examples(frame: pd.DataFrame, column: str, *, limit: int = 10) -> list[str]:
    if column not in frame.columns or frame.empty:
        return []
    return [str(value) for value in frame[column].head(limit).tolist()]


def _markdown_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "- none"
    return "\n".join(f"- `{key}`: {value}" for key, value in counts.items())


def _relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)
