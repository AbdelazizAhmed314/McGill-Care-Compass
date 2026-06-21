"""Validate the v1 actionable (enriched) service dataset.

Checks the enriched dataset that ``build_actionable_service_records.py`` produces:
base fields preserved, enrichment fields present, status values valid, the v1
enrichment target met (>= 15 enriched), enriched rows carry real source-grounded
content with no generic "go to the website" next steps, high-risk rows keep their
limitation wording, and CSV/JSON stay in sync.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATASETS = ROOT / "data" / "datasets"
DATASET_CSV = DATASETS / "actionable_service_records.csv"
DATASET_JSON = DATASETS / "actionable_service_records.json"

MIN_ENRICHED = 15

BASE_FIELDS = [
    "record_id",
    "service_name",
    "category_id",
    "category_label",
    "student_need",
    "official_source_url",
    "source_publisher",
    "last_verified_date",
    "limitations",
]
ENRICHMENT_FIELDS = [
    "actionable_summary",
    "actionable_next_step",
    "eligibility_or_requirements",
    "access_steps",
    "costs_or_coverage",
    "contact_or_location",
    "source_evidence_excerpt",
    "extraction_status",
    "content_last_checked_at",
    "source_content_hash",
]
ALLOWED_STATUSES = {"enriched", "partial", "fetch_failed", "not_targeted"}
ENRICHED_REQUIRED = [
    "actionable_summary",
    "actionable_next_step",
    "access_steps",
    "source_evidence_excerpt",
    "content_last_checked_at",
    "source_content_hash",
]
HIGH_RISK_CATEGORIES = {
    "health_care",
    "mental_health",
    "insurance",
    "immigration_status",
    "tax",
    "finances",
    "safety_urgent",
}
GENERIC_NEXT_STEP_PATTERNS = (
    "review the official",
    "review this",
    "see the next steps",
    "visit the website",
    "see the official",
    "check the website",
    "go to the website",
    "review the website",
    "review the appropriate",
)


def is_url(value: str) -> bool:
    """Return True when a value is an absolute HTTP(S) URL."""

    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def require(condition: bool, message: str, errors: list[str]) -> None:
    """Collect a failure without aborting the rest of the checks."""

    if not condition:
        errors.append(message)


def validate() -> list[str]:
    """Return all validation errors for the enriched dataset."""

    errors: list[str] = []
    require(DATASET_CSV.exists(), f"Missing dataset: {DATASET_CSV.relative_to(ROOT)}", errors)
    require(DATASET_JSON.exists(), f"Missing dataset: {DATASET_JSON.relative_to(ROOT)}", errors)
    if errors:
        return errors

    records = pd.read_csv(DATASET_CSV).fillna("")

    missing_base = [field for field in BASE_FIELDS if field not in records.columns]
    require(not missing_base, f"Missing base columns: {missing_base}", errors)
    missing_enrich = [field for field in ENRICHMENT_FIELDS if field not in records.columns]
    require(not missing_enrich, f"Missing enrichment columns: {missing_enrich}", errors)
    if missing_base or missing_enrich:
        return errors

    require(records["record_id"].is_unique, "Duplicate record_id values present", errors)

    bad_status = sorted(set(records["extraction_status"]) - ALLOWED_STATUSES)
    require(not bad_status, f"Invalid extraction_status values: {bad_status}", errors)

    invalid_urls = [
        row.record_id
        for row in records.itertuples(index=False)
        if not is_url(str(row.official_source_url))
    ]
    require(not invalid_urls, f"Invalid official_source_url for: {invalid_urls}", errors)

    enriched = records[records["extraction_status"] == "enriched"]
    require(
        len(enriched) >= MIN_ENRICHED,
        f"Expected at least {MIN_ENRICHED} enriched records, found {len(enriched)}",
        errors,
    )

    for field in ENRICHED_REQUIRED:
        blank = enriched[enriched[field].astype(str).str.strip().eq("")]
        require(
            blank.empty,
            f"Enriched records missing `{field}`: {blank['record_id'].tolist()}",
            errors,
        )

    generic = [
        row.record_id
        for row in enriched.itertuples(index=False)
        if any(pattern in str(row.actionable_next_step).lower() for pattern in GENERIC_NEXT_STEP_PATTERNS)
    ]
    require(
        not generic,
        f"Enriched records have generic 'visit the website' next steps: {generic}",
        errors,
    )

    high_risk_missing = [
        row.record_id
        for row in enriched.itertuples(index=False)
        if row.category_id in HIGH_RISK_CATEGORIES and not str(row.limitations).strip()
    ]
    require(
        not high_risk_missing,
        f"High-risk enriched records missing limitation wording: {high_risk_missing}",
        errors,
    )

    mirror = pd.DataFrame(json.loads(DATASET_JSON.read_text(encoding="utf-8"))).fillna("")
    require(
        list(records["record_id"]) == list(mirror.get("record_id", [])),
        "CSV and JSON record_id order differ",
        errors,
    )
    if list(records["record_id"]) == list(mirror.get("record_id", [])):
        mismatches = 0
        for column in records.columns:
            if column in mirror.columns:
                csv_values = records[column].astype(str).tolist()
                json_values = mirror[column].astype(str).tolist()
                mismatches += sum(a != b for a, b in zip(csv_values, json_values))
        require(mismatches == 0, f"CSV/JSON field mismatches: {mismatches}", errors)

    return errors


def main() -> None:
    """Run validation and print a summary."""

    errors = validate()
    if errors:
        print("Actionable dataset validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    records = pd.read_csv(DATASET_CSV).fillna("")
    status_counts = Counter(records["extraction_status"])
    print("Actionable dataset validation passed.")
    print(f"Records: {len(records)}")
    for status in ("enriched", "partial", "fetch_failed", "not_targeted"):
        print(f"- {status}: {status_counts.get(status, 0)}")


if __name__ == "__main__":
    main()
