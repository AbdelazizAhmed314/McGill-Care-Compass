"""Deterministic maintenance analysis for governed RAG artifacts."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from mcgill_care_compass.retrieval import CATEGORY_LABELS

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "data" / "silver" / "datasets"
PAGES_CSV = DATASETS_DIR / "rag_pages.csv"
LINKS_CSV = DATASETS_DIR / "rag_links.csv"
CHUNKS_CSV = DATASETS_DIR / "rag_chunks.csv"
FAILED_SOURCE_DISPOSITIONS_CSV = (
    ROOT / "data" / "source-inputs" / "rag_failed_source_dispositions.csv"
)
REQUIRED_SOURCE_URLS_CSV = ROOT / "data" / "source-inputs" / "rag_required_source_urls.csv"
OUTPUT_DIR = ROOT / "data" / "silver" / "maintenance"
DEFAULT_JSON_REPORT = OUTPUT_DIR / "rag_maintenance_report.json"
DEFAULT_MARKDOWN_REPORT = OUTPUT_DIR / "rag_maintenance_report.md"
NONBLOCKING_DISPOSITION = "reviewed_nonblocking"
DISPOSITION_MAX_AGE_DAYS = 30
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)?")
NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
BOILERPLATE_RE = re.compile(
    r"column 1|faculty & staff|join our team|related services|quick links",
    re.IGNORECASE,
)
ACTION_FIELDS = (
    "has_contact_info",
    "has_required_docs",
    "has_eligibility",
    "has_costs_coverage",
    "has_location",
    "has_deadlines",
    "has_booking_steps",
)
GUARDRAIL_ONLY_CATEGORIES = {"safety_urgent"}
REQUIRED_FIELDS = {
    "pages": (
        "canonical_url",
        "source_group",
        "source_publisher",
        "authority_level",
        "category_id",
        "retrieved_at",
        "terms_url",
        "licence_or_terms",
    ),
    "links": (
        "source_canonical_url",
        "target_canonical_url",
        "link_type",
        "crawl_decision",
    ),
    "chunks": (
        "chunk_id",
        "canonical_url",
        "chunk_text",
        "category_id",
        "source_group",
        "source_publisher",
        "retrieved_at",
        "terms_url",
        "licence_or_terms",
        "review_status",
        "vector_id",
    ),
}


def read_csv_records(path: Path) -> list[dict[str, str]]:
    """Read a CSV into normalized string dictionaries."""

    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {str(key): str(value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def build_maintenance_report(
    pages: list[dict[str, str]],
    links: list[dict[str, str]],
    chunks: list[dict[str, str]],
    *,
    failed_source_dispositions: dict[str, dict[str, str]] | None = None,
    required_source_urls: set[str] | None = None,
    as_of: date | None = None,
    stale_after_days: int = 30,
    example_limit: int = 25,
) -> dict[str, Any]:
    """Classify freshness, failures, missing data, coverage, and chunk quality."""

    report_date = as_of or datetime.now(UTC).date()
    freshness = _freshness_report(
        pages,
        as_of=report_date,
        stale_after_days=stale_after_days,
        example_limit=example_limit,
    )
    failed_sources = _failed_source_report(
        pages,
        chunks,
        dispositions=failed_source_dispositions or {},
        required_source_urls=required_source_urls or set(),
        as_of=report_date,
    )
    skipped_links = _skipped_link_report(links, example_limit=example_limit)
    missing_data = {
        "pages": _missing_report(pages, REQUIRED_FIELDS["pages"], example_limit),
        "links": _missing_report(links, REQUIRED_FIELDS["links"], example_limit),
        "chunks": _missing_report(chunks, REQUIRED_FIELDS["chunks"], example_limit),
    }
    coverage = _coverage_report(pages, chunks)
    quality = _chunk_quality_report(chunks, example_limit=example_limit)
    error_count = (
        failed_sources["blocking_count"]
        + sum(section["rows_with_missing_data"] for section in missing_data.values())
        + len(coverage.get("categories_without_pages", []))
        + len(coverage.get("categories_without_chunks", []))
    )
    warning_count = (
        freshness["changed_count"]
        + freshness["new_count"]
        + freshness["stale_count"]
        + failed_sources["nonblocking_count"]
        + sum(item["count"] for item in quality.values())
    )
    severity_counts = {
        "error": int(error_count),
        "warning": int(warning_count),
        "info": int(skipped_links["count"]),
    }
    needs_attention = bool(error_count or warning_count)
    return {
        "report_schema_version": "3",
        "as_of": report_date.isoformat(),
        "stale_after_days": stale_after_days,
        "pipeline_run_id": _single_value(pages, "pipeline_run_id"),
        "source_generated_at": _single_value(pages, "generated_at"),
        "requires_attention": needs_attention,
        "has_errors": bool(error_count),
        "severity_counts": severity_counts,
        "counts": {"pages": len(pages), "links": len(links), "chunks": len(chunks)},
        "source_freshness": freshness,
        "failed_sources": failed_sources,
        "intentional_link_skips": skipped_links,
        "missing_data": missing_data,
        "category_coverage": coverage,
        "chunk_quality": quality,
    }


def generate_maintenance_reports(
    *,
    pages_csv: Path = PAGES_CSV,
    links_csv: Path = LINKS_CSV,
    chunks_csv: Path = CHUNKS_CSV,
    failed_source_dispositions_csv: Path = FAILED_SOURCE_DISPOSITIONS_CSV,
    required_source_urls_csv: Path = REQUIRED_SOURCE_URLS_CSV,
    json_path: Path = DEFAULT_JSON_REPORT,
    markdown_path: Path = DEFAULT_MARKDOWN_REPORT,
    as_of: date | None = None,
    stale_after_days: int = 30,
) -> dict[str, Any]:
    """Analyze current artifacts and write machine- and human-readable reports."""

    report = build_maintenance_report(
        read_csv_records(pages_csv),
        read_csv_records(links_csv),
        read_csv_records(chunks_csv),
        failed_source_dispositions=_read_failed_source_dispositions(
            failed_source_dispositions_csv
        ),
        required_source_urls=_read_required_source_urls(required_source_urls_csv),
        as_of=as_of,
        stale_after_days=stale_after_days,
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(format_maintenance_markdown(report), encoding="utf-8")
    return report


def format_maintenance_markdown(report: dict[str, Any]) -> str:
    """Render a concise maintenance report with actionable record examples."""

    freshness = report["source_freshness"]
    failed = report["failed_sources"]
    skipped = report["intentional_link_skips"]
    coverage = report["category_coverage"]
    quality = report["chunk_quality"]
    lines = [
        "# RAG Maintenance Report",
        "",
        f"- Status: {'REVIEW REQUIRED' if report['requires_attention'] else 'OK'}",
        f"- Errors: {report['severity_counts']['error']}",
        f"- Warnings: {report['severity_counts']['warning']}",
        f"- Informational findings: {report['severity_counts']['info']}",
        f"- As of: {report['as_of']}",
        f"- Pipeline run: {report['pipeline_run_id'] or 'unknown'}",
        f"- Pages / links / chunks: {report['counts']['pages']} / "
        f"{report['counts']['links']} / {report['counts']['chunks']}",
        "",
        "## Source freshness",
        "",
        f"- Unchanged: {freshness['drift_counts'].get('unchanged', 0)}",
        f"- Changed: {freshness['changed_count']}",
        f"- New: {freshness['new_count']}",
        f"- Fetch failed: {freshness['fetch_failed_count']}",
        f"- Older than {report['stale_after_days']} days: {freshness['stale_count']}",
        f"- Missing optional source-updated date: {freshness['source_updated_at_missing_count']}",
        "",
        "## Failed sources and link decisions",
        "",
        f"- Failed page fetches: {failed['count']}",
        f"- Blocking failed pages: {failed['blocking_count']}",
        f"- Reviewed nonblocking failed pages: {failed['nonblocking_count']}",
        "- Configured additional required sources: "
        f"{failed['configured_required_source_count']}",
        f"- Intentionally skipped/not-crawled links: {skipped['count']}",
        "- Failed pages block by default. A zero-chunk failure becomes a warning only "
        "when it has a complete reviewed_nonblocking disposition.",
        f"- Disposition reviews expire after {failed['review_max_age_days']} days and "
        "must identify an active official replacement in the same category.",
        "- Seed pages cannot receive a nonblocking disposition.",
        "- A failed page with active chunks always blocks, regardless of disposition.",
        "- Skipped links are reported separately and are not classified as broken.",
    ]
    for label, records, fields in (
        ("Changed examples", freshness["changed_records"], ("canonical_url", "retrieved_at")),
        ("New examples", freshness["new_records"], ("canonical_url", "retrieved_at")),
        (
            "Fetch-failed drift examples",
            freshness["fetch_failed_records"],
            ("canonical_url", "retrieved_at"),
        ),
        ("Stale examples", freshness["stale_records"], ("canonical_url", "age_days")),
    ):
        if records:
            lines.extend(["", f"### {label}"])
            lines.extend(_record_lines(records, fields))
    lines.extend(
        _record_lines(
            failed["records"],
            (
                "canonical_url",
                "http_status",
                "fetch_error",
                "active_chunk_count",
                "classification",
                "disposition_reason",
                "reviewed_at",
                "review_reference",
                "disposition_pipeline_run_id",
                "replacement_url",
                "replacement_active_chunk_count",
                "disposition_validation_errors",
            ),
        )
    )
    if skipped["by_reason"]:
        lines.extend(["", "### Intentional skip reasons", ""])
        for reason, count in skipped["by_reason"].items():
            lines.append(f"- {reason}: {count}")
        lines.extend(
            _record_lines(
                skipped["examples"],
                ("target_canonical_url", "crawl_decision", "skip_reason"),
            )
        )
    lines.extend(["", "## Missing required metadata", ""])
    for dataset, details in report["missing_data"].items():
        lines.append(f"- {dataset}: {details['rows_with_missing_data']} rows")
        for field, count in details["missing_by_field"].items():
            if count:
                lines.append(f"  - {field}: {count}")
        lines.extend(_record_lines(details["examples"], ("identifier", "missing_fields")))
    lines.extend(["", "## Category coverage", ""])
    for category_id, details in coverage["by_category"].items():
        lines.append(
            f"- {category_id}: {details['pages']} pages, {details['chunks']} chunks "
            f"({details['mode']})"
        )
    if coverage["categories_without_chunks"]:
        lines.append(
            "- Categories without chunks: " + ", ".join(coverage["categories_without_chunks"])
        )
    lines.extend(["", "## Chunk quality", ""])
    for name, details in quality.items():
        lines.append(f"- {name}: {details['count']}")
        for example in details["examples"]:
            lines.append(
                f"  - chunk_id={example['chunk_id']}; canonical_url={example['canonical_url']}"
            )
    lines.append("")
    return "\n".join(lines)


def _freshness_report(
    pages: list[dict[str, str]],
    *,
    as_of: date,
    stale_after_days: int,
    example_limit: int,
) -> dict[str, Any]:
    drift_counts = Counter(row.get("drift_status", "") or "missing" for row in pages)
    drift_records: dict[str, list[dict[str, str]]] = {}
    for status in ("changed", "new", "fetch_failed"):
        drift_records[status] = [
            {
                "canonical_url": row.get("canonical_url", ""),
                "retrieved_at": row.get("retrieved_at", ""),
                "source_updated_at": row.get("source_updated_at", ""),
            }
            for row in pages
            if row.get("drift_status") == status
        ][:example_limit]
    stale: list[dict[str, Any]] = []
    for row in pages:
        retrieved = _parse_date(row.get("retrieved_at", ""))
        if retrieved is None:
            continue
        age = (as_of - retrieved).days
        if age > stale_after_days:
            stale.append(
                {
                    "canonical_url": row.get("canonical_url", ""),
                    "retrieved_at": row.get("retrieved_at", ""),
                    "age_days": age,
                }
            )
    return {
        "drift_counts": dict(sorted(drift_counts.items())),
        "changed_count": drift_counts.get("changed", 0),
        "new_count": drift_counts.get("new", 0),
        "fetch_failed_count": drift_counts.get("fetch_failed", 0),
        "source_updated_at_present_count": sum(bool(row.get("source_updated_at")) for row in pages),
        "source_updated_at_missing_count": sum(not row.get("source_updated_at") for row in pages),
        "changed_records": drift_records["changed"],
        "new_records": drift_records["new"],
        "fetch_failed_records": drift_records["fetch_failed"],
        "stale_count": len(stale),
        "stale_records": stale[:example_limit],
    }


def _failed_source_report(
    pages: list[dict[str, str]],
    chunks: list[dict[str, str]],
    *,
    dispositions: dict[str, dict[str, str]],
    required_source_urls: set[str],
    as_of: date,
) -> dict[str, Any]:
    dispositions_by_url = {
        _normalize_url(url): disposition for url, disposition in dispositions.items()
    }
    normalized_required_source_urls = {
        _normalize_url(url) for url in required_source_urls if url
    }
    active_chunk_counts = Counter(
        _normalize_url(row.get("canonical_url", ""))
        for row in chunks
        if row.get("canonical_url")
    )
    pages_by_url = {
        _normalize_url(row.get("canonical_url", "")): row
        for row in pages
        if row.get("canonical_url")
    }
    failed = []
    for row in pages:
        if _page_fetch_failed(row):
            canonical_url = row.get("canonical_url", "")
            normalized_url = _normalize_url(canonical_url)
            active_chunk_count = active_chunk_counts.get(normalized_url, 0)
            disposition = dispositions_by_url.get(normalized_url, {})
            validation_errors = _nonblocking_disposition_errors(
                disposition,
                row,
                as_of=as_of,
                pages_by_url=pages_by_url,
                active_chunk_counts=active_chunk_counts,
                required_source_urls=normalized_required_source_urls,
            )
            classification = (
                NONBLOCKING_DISPOSITION
                if not active_chunk_count and not validation_errors
                else "blocking"
            )
            replacement_url = disposition.get("replacement_url", "")
            failed.append(
                {
                    "canonical_url": canonical_url,
                    "http_status": row.get("http_status", ""),
                    "fetch_error": row.get("fetch_error", ""),
                    "drift_status": row.get("drift_status", ""),
                    "active_chunk_count": active_chunk_count,
                    "classification": classification,
                    "disposition": disposition.get("disposition", ""),
                    "disposition_reason": disposition.get("reason", ""),
                    "reviewed_at": disposition.get("reviewed_at", ""),
                    "review_reference": disposition.get("review_reference", ""),
                    "disposition_pipeline_run_id": disposition.get(
                        "pipeline_run_id", ""
                    ),
                    "replacement_url": replacement_url,
                    "replacement_active_chunk_count": active_chunk_counts.get(
                        _normalize_url(replacement_url), 0
                    ),
                    "disposition_validation_errors": validation_errors,
                }
            )
    blocking_count = sum(row["classification"] == "blocking" for row in failed)
    return {
        "count": len(failed),
        "blocking_count": blocking_count,
        "nonblocking_count": len(failed) - blocking_count,
        "review_max_age_days": DISPOSITION_MAX_AGE_DAYS,
        "configured_required_source_count": len(normalized_required_source_urls),
        "records": failed,
    }


def _read_failed_source_dispositions(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    return {
        row["canonical_url"]: row
        for row in read_csv_records(path)
        if row.get("canonical_url")
    }


def _read_required_source_urls(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        row["canonical_url"]
        for row in read_csv_records(path)
        if row.get("canonical_url")
    }


def _nonblocking_disposition_errors(
    disposition: dict[str, str],
    page: dict[str, str],
    *,
    as_of: date,
    pages_by_url: dict[str, dict[str, str]],
    active_chunk_counts: Counter[str],
    required_source_urls: set[str],
) -> list[str]:
    errors = []
    if disposition.get("disposition") != NONBLOCKING_DISPOSITION:
        errors.append("missing_or_invalid_disposition")
    if not disposition.get("reason"):
        errors.append("missing_reason")

    reviewed_at = _parse_date(disposition.get("reviewed_at", ""))
    if reviewed_at is None:
        errors.append("missing_or_invalid_reviewed_at")
    elif reviewed_at > as_of:
        errors.append("reviewed_at_is_in_future")
    elif (as_of - reviewed_at).days > DISPOSITION_MAX_AGE_DAYS:
        errors.append("review_expired")

    if not disposition.get("review_reference"):
        errors.append("missing_review_reference")
    if not page.get("pipeline_run_id"):
        errors.append("missing_page_pipeline_run_id")
    elif disposition.get("pipeline_run_id") != page.get("pipeline_run_id"):
        errors.append("pipeline_run_id_mismatch")

    canonical_url = _normalize_url(page.get("canonical_url", ""))
    if canonical_url and canonical_url == _normalize_url(page.get("seed_url", "")):
        errors.append("seed_page_cannot_be_nonblocking")
    if canonical_url in required_source_urls:
        errors.append("configured_required_source_cannot_be_nonblocking")

    replacement_url = _normalize_url(disposition.get("replacement_url", ""))
    replacement_page = pages_by_url.get(replacement_url)
    if not replacement_url:
        errors.append("missing_replacement_url")
    elif replacement_url == canonical_url:
        errors.append("replacement_matches_failed_source")
    elif replacement_page is None:
        errors.append("replacement_not_in_page_manifest")
    else:
        if _page_fetch_failed(replacement_page):
            errors.append("replacement_fetch_failed")
        if not active_chunk_counts.get(replacement_url, 0):
            errors.append("replacement_has_no_active_chunks")
        if replacement_page.get("category_id") != page.get("category_id"):
            errors.append("replacement_category_mismatch")
        if not replacement_page.get("authority_level", "").startswith("official_"):
            errors.append("replacement_is_not_official")
        if replacement_page.get("pipeline_run_id") != page.get("pipeline_run_id"):
            errors.append("replacement_pipeline_run_id_mismatch")
    return errors


def _page_fetch_failed(page: dict[str, str]) -> bool:
    status = _integer(page.get("http_status", ""))
    return bool(
        page.get("fetch_error")
        or page.get("drift_status") == "fetch_failed"
        or (status is not None and not 200 <= status < 400)
    )


def _normalize_url(value: str) -> str:
    return value.strip().rstrip("/")


def _skipped_link_report(links: list[dict[str, str]], *, example_limit: int) -> dict[str, Any]:
    skipped = [
        row
        for row in links
        if row.get("crawl_decision") != "queued" or bool(row.get("skip_reason"))
    ]
    reasons = Counter(row.get("skip_reason", "") or "not_queued" for row in skipped)
    examples = [
        {
            "target_canonical_url": row.get("target_canonical_url", ""),
            "crawl_decision": row.get("crawl_decision", ""),
            "skip_reason": row.get("skip_reason", ""),
        }
        for row in skipped[:example_limit]
    ]
    return {"count": len(skipped), "by_reason": dict(sorted(reasons.items())), "examples": examples}


def _missing_report(
    rows: list[dict[str, str]], required_fields: tuple[str, ...], example_limit: int
) -> dict[str, Any]:
    missing_by_field = {
        field: sum(not row.get(field, "").strip() for row in rows) for field in required_fields
    }
    missing_rows = []
    for index, row in enumerate(rows):
        fields = [field for field in required_fields if not row.get(field, "").strip()]
        if fields:
            missing_rows.append(
                {
                    "row": index + 2,
                    "identifier": row.get("chunk_id")
                    or row.get("canonical_url")
                    or row.get("target_canonical_url")
                    or "",
                    "missing_fields": fields,
                }
            )
    return {
        "rows_with_missing_data": len(missing_rows),
        "missing_by_field": missing_by_field,
        "examples": missing_rows[:example_limit],
    }


def _coverage_report(pages: list[dict[str, str]], chunks: list[dict[str, str]]) -> dict[str, Any]:
    page_counts = Counter(row.get("category_id", "") for row in pages if row.get("category_id"))
    chunk_counts = Counter(row.get("category_id", "") for row in chunks if row.get("category_id"))
    category_ids = sorted(set(CATEGORY_LABELS) | set(page_counts) | set(chunk_counts))
    by_category = {
        category_id: {
            "label": CATEGORY_LABELS.get(category_id, "Unknown category"),
            "pages": page_counts.get(category_id, 0),
            "chunks": chunk_counts.get(category_id, 0),
            "mode": ("guardrail_only" if category_id in GUARDRAIL_ONLY_CATEGORIES else "retrieval"),
        }
        for category_id in category_ids
    }
    return {
        "by_category": by_category,
        "categories_without_pages": [
            key
            for key, value in by_category.items()
            if value["mode"] == "retrieval" and not value["pages"]
        ],
        "categories_without_chunks": [
            key
            for key, value in by_category.items()
            if value["mode"] == "retrieval" and not value["chunks"]
        ],
        "guardrail_only_categories": sorted(GUARDRAIL_ONLY_CATEGORIES),
    }


def _chunk_quality_report(
    chunks: list[dict[str, str]], *, example_limit: int
) -> dict[str, dict[str, Any]]:
    findings: dict[str, list[dict[str, str]]] = defaultdict(list)
    normalized_counts = Counter(
        NORMALIZE_RE.sub(" ", row.get("chunk_text", "").casefold()).strip() for row in chunks
    )
    for row in chunks:
        chunk_id = row.get("chunk_id", "")
        text = row.get("chunk_text", "")
        word_count = len(WORD_RE.findall(text))
        actionable = any(_truthy(row.get(field, "")) for field in ACTION_FIELDS)
        normalized = NORMALIZE_RE.sub(" ", text.casefold()).strip()
        boilerplate = bool(BOILERPLATE_RE.search(text))
        nearby_link_count = row.get("nearby_links", "").count("http")
        finding = {
            "chunk_id": chunk_id,
            "canonical_url": row.get("canonical_url", ""),
        }
        if word_count < 15 and not actionable:
            findings["very_short_non_actionable"].append(finding)
        if word_count > 350:
            findings["oversized_over_350_words"].append(finding)
        if normalized and normalized_counts[normalized] > 1:
            findings["duplicate_normalized_text"].append(finding)
        if boilerplate:
            findings["boilerplate_pattern"].append(finding)
        if boilerplate or (nearby_link_count >= 5 and word_count < 120):
            findings["navigation_heavy"].append(finding)
    names = (
        "very_short_non_actionable",
        "oversized_over_350_words",
        "duplicate_normalized_text",
        "boilerplate_pattern",
        "navigation_heavy",
    )
    return {
        name: {
            "count": len(findings[name]),
            "example_chunk_ids": [item["chunk_id"] for item in findings[name][:example_limit]],
            "examples": findings[name][:example_limit],
        }
        for name in names
    }


def _parse_date(value: str) -> date | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        return None


def _integer(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _truthy(value: str) -> bool:
    return value.casefold() in {"1", "true", "yes", "y"}


def _single_value(rows: list[dict[str, str]], field: str) -> str:
    values = {row.get(field, "") for row in rows if row.get(field)}
    return next(iter(values)) if len(values) == 1 else ""


def _record_lines(records: list[dict[str, Any]], fields: tuple[str, ...]) -> list[str]:
    if not records:
        return []
    lines = [""]
    for record in records:
        details = "; ".join(f"{field}={record.get(field, '')}" for field in fields)
        lines.append(f"- {details}")
    return lines
