"""Validate the curated service directory against the June 21 milestone."""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "data" / "datasets" / "curated_service_records.csv"

REQUIRED_FIELDS = [
    "record_id",
    "service_name",
    "category_id",
    "category_label",
    "student_need",
    "intended_users",
    "access_method",
    "recommended_next_step",
    "limitations",
    "official_source_url",
    "source_name",
    "source_publisher",
    "source_license_or_terms",
    "source_retrieved_at",
    "source_record_id",
    "last_verified_date",
    "review_status",
]

TAXONOMY = {
    "health_care": "Healthcare access",
    "mental_health": "Mental health and wellbeing",
    "insurance": "Health insurance and coverage",
    "immigration_status": "Immigration and legal status",
    "housing": "Housing and basic needs",
    "academics": "Academic and advising support",
    "finances": "Financial aid and affordability",
    "work_career": "Work and career support",
    "tax": "Tax filing and residency information",
    "documents_admin": "Campus documents and administration",
    "language_integration": "Language and integration",
    "safety_urgent": "Urgent or safety-related help",
}


def is_url(value: str) -> bool:
    """Return True when a value looks like an absolute HTTP(S) URL."""

    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def require(condition: bool, message: str, errors: list[str]) -> None:
    """Collect validation failures without aborting the first check."""

    if not condition:
        errors.append(message)


def validate() -> list[str]:
    """Return all validation errors for the curated service directory."""

    errors: list[str] = []
    require(DATASET.exists(), f"Missing dataset: {DATASET.relative_to(ROOT)}", errors)
    if errors:
        return errors

    records = pd.read_csv(DATASET).fillna("")
    require(len(records) >= 40, f"Expected at least 40 records, found {len(records)}", errors)

    missing_columns = [field for field in REQUIRED_FIELDS if field not in records.columns]
    require(not missing_columns, f"Missing required columns: {missing_columns}", errors)
    if missing_columns:
        return errors

    for field in REQUIRED_FIELDS:
        missing = records[records[field].astype(str).str.strip().eq("")]
        require(missing.empty, f"Field `{field}` has {len(missing)} blank values", errors)

    duplicate_ids = records[records["record_id"].duplicated()]["record_id"].tolist()
    require(not duplicate_ids, f"Duplicate record_id values: {duplicate_ids}", errors)

    invalid_urls = [
        record_id
        for record_id, url in zip(records["record_id"], records["official_source_url"])
        if not is_url(str(url))
    ]
    require(not invalid_urls, f"Invalid official_source_url values for: {invalid_urls}", errors)

    invalid_terms_urls = [
        record_id
        for record_id, url in zip(records["record_id"], records["source_license_or_terms"])
        if not is_url(str(url))
    ]
    require(
        not invalid_terms_urls,
        f"Invalid source_license_or_terms URLs for: {invalid_terms_urls}",
        errors,
    )

    invalid_categories = sorted(set(records["category_id"]) - set(TAXONOMY))
    require(not invalid_categories, f"Invalid category_id values: {invalid_categories}", errors)

    mismatched_labels = [
        row.record_id
        for row in records.itertuples(index=False)
        if TAXONOMY.get(row.category_id) != row.category_label
    ]
    require(not mismatched_labels, f"Category label mismatch for: {mismatched_labels}", errors)

    invalid_dates = []
    for row in records.itertuples(index=False):
        try:
            date.fromisoformat(str(row.last_verified_date))
        except ValueError:
            invalid_dates.append(row.record_id)
    require(not invalid_dates, f"Invalid last_verified_date values for: {invalid_dates}", errors)

    category_count = records["category_id"].nunique()
    require(category_count >= 8, f"Expected at least 8 categories, found {category_count}", errors)

    mcgill_count = (records["source_publisher"] == "McGill University").sum()
    require(mcgill_count >= 20, f"Expected at least 20 McGill records, found {mcgill_count}", errors)

    healthcare_wellness_count = records["category_id"].isin({"health_care", "mental_health"}).sum()
    require(
        healthcare_wellness_count >= 10,
        "Expected at least 10 healthcare/wellness records, "
        f"found {healthcare_wellness_count}",
        errors,
    )

    odhf_rows = records[records["source_name"].str.contains("ODHF", case=False, na=False)]
    missing_odhf_provenance = odhf_rows[
        odhf_rows[["source_publisher", "source_license_or_terms", "source_record_id"]]
        .astype(str)
        .apply(lambda column: column.str.strip().eq(""))
        .any(axis=1)
    ]
    require(
        missing_odhf_provenance.empty,
        "ODHF-derived records are missing required provenance: "
        f"{missing_odhf_provenance['record_id'].tolist()}",
        errors,
    )

    return errors


def main() -> None:
    """Run validation and print a milestone-oriented summary."""

    errors = validate()
    if errors:
        print("Curated service directory validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    records = pd.read_csv(DATASET).fillna("")
    category_counts = Counter(records["category_id"])
    print("Curated service directory validation passed.")
    print(f"Records: {len(records)}")
    print(f"Categories: {records['category_id'].nunique()}")
    print(f"McGill records: {(records['source_publisher'] == 'McGill University').sum()}")
    print(
        "Healthcare/wellness records: "
        f"{records['category_id'].isin({'health_care', 'mental_health'}).sum()}"
    )
    print("Category counts:")
    for category_id, count in sorted(category_counts.items()):
        print(f"- {category_id}: {count}")


if __name__ == "__main__":
    main()
