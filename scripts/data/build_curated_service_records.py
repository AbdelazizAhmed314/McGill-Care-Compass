"""Build the June 21 curated service directory milestone.

This script converts selected, reviewed source-evidence rows into the
production ServiceRecord shape used by the app scaffold.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATASETS = ROOT / "data" / "datasets"
REPORTS = ROOT / "data" / "reports"

OUTPUT_CSV = DATASETS / "curated_service_records.csv"
OUTPUT_JSON = DATASETS / "curated_service_records.json"
QUALITY_REPORT = REPORTS / "curated_service_directory_quality_report.md"

LAST_VERIFIED_DATE = "2026-06-19"
CURATED_STATUS = "curated_for_directory_milestone"

FIELDNAMES = [
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

SOURCE_CATEGORY_MAP = {
    "academics": "academics",
    "administration": "documents_admin",
    "community": "language_integration",
    "employment": "work_career",
    "financial_aid": "finances",
    "health_insurance": "insurance",
    "healthcare": "health_care",
    "housing": "housing",
    "immigration": "immigration_status",
    "tax": "tax",
    "wellness": "mental_health",
}

SOURCE_TERMS = {
    "Canada Revenue Agency": "https://www.canada.ca/en/transparency/terms.html",
    "Gouvernement du Québec": "https://www.quebec.ca/en/copyright",
    "McGill University": "https://www.mcgill.ca/copyright/",
}

LIMITATIONS = {
    "academics": (
        "The navigator does not make academic decisions or interpret individual program "
        "requirements; confirm details with the official advising or faculty source."
    ),
    "documents_admin": (
        "Administrative requirements, fees, and processing times can change; confirm details "
        "through the official McGill page before acting."
    ),
    "finances": (
        "The navigator does not determine financial-aid eligibility or award amounts; confirm "
        "requirements with the official funding office."
    ),
    "health_care": (
        "The navigator does not diagnose, triage symptoms, or confirm service availability; "
        "for emergencies call 911 or go to an emergency department."
    ),
    "housing": (
        "The navigator does not provide legal housing advice or determine tenant rights; "
        "confirm obligations and options with official housing or tenant resources."
    ),
    "immigration_status": (
        "The navigator does not interpret immigration status or determine eligibility; use "
        "official sources and qualified advisors for individual decisions."
    ),
    "insurance": (
        "Coverage, exemptions, claims, and costs must be confirmed through the official "
        "insurance source."
    ),
    "language_integration": (
        "Program availability, eligibility, and language options may change; confirm details "
        "with the official provider."
    ),
    "mental_health": (
        "This record is not medical or crisis advice; for urgent safety concerns call 911 or "
        "use official urgent-support resources."
    ),
    "tax": (
        "The navigator does not determine tax residency, filing obligations, credits, or "
        "benefits; confirm with official CRA guidance or a qualified tax professional."
    ),
    "work_career": (
        "The navigator does not determine work authorization or job eligibility; confirm "
        "requirements with official McGill or government sources."
    ),
}

SELECTED_CRA_RECORD_IDS = {
    "4d483ab7c367b2e79e10",  # Determining your residency status
    "861a9765bdbe41051240",  # newcomers to Canada
    "9906aa98882bf665ec84",  # Common deductions and credits for students
    "192ad052bc88412b5a17",  # Free tax clinics
    "0740a11ecb8225443bbc",  # Who has to file a return
}

SELECTED_QUEBEC_HEALTH_RECORD_IDS = {
    "bf5d5325d104f2c835fd",  # Getting a medical consultation
    "c23a08cb50d9647f8f62",  # Primary care health and social services
    "cad3979bb02b4ff55ada",  # Primary Care Access Point
    "6dbee08280a519a0dd2b",  # Quebec Family Doctor Finder
    "be4c05eb575806d3adf6",  # Registering to the waiting list
}

SELECTED_QUEBEC_HOUSING_RECORD_IDS = {
    # Renter-relevant settlement topics for newcomer students. The two "buying a
    # house/condominium" rows were dropped in curation review: they are near-duplicates
    # of each other and low-relevance for students, who overwhelmingly rent.
    "71d4e9ac089ca3ba69e6",  # Finding housing
    "3c488317249924fa8aaa",  # Information to provide
    "3058a95e44eb27e11ed4",  # Refusal to rent
}

# Proposal-sample rows dropped during curation review:
# - scraped navigation-label fragments that are not real services, and
# - one record that duplicates a higher-quality curated record (mcgill-ihi) and was
#   filed under the wrong category.
EXCLUDED_PROPOSAL_RECORD_IDS = {
    "5fba4d3a3ed5502729e4",  # "Questions?" — nav link on the Student Aid page
    "1e4d918ddcd6205740d5",  # "Current Students" — Service Point menu label
    "4e0c2c9e5cb715580f3a",  # "Arts & Science Students" — Service Point menu label
    "25efee510c26387c0bfd",  # "International Health Insurance" — duplicate of mcgill-ihi
}


def clean(value: Any) -> str:
    """Return a stable empty-string-normalized value."""

    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def category_id(source_category: str) -> str:
    """Map source evidence categories into the locked taxonomy."""

    mapped = SOURCE_CATEGORY_MAP[source_category]
    if mapped not in TAXONOMY:
        raise ValueError(f"Unsupported category after mapping: {mapped}")
    return mapped


def source_terms(publisher: str) -> str:
    """Return the terms/provenance reference for a source publisher."""

    return SOURCE_TERMS.get(publisher, "Source terms not identified; verify before reuse.")


def normalize_timestamp(value: Any) -> str:
    """Normalize a source timestamp/date to the retained evidence value."""

    return clean(value) or LAST_VERIFIED_DATE


def official_url(*candidates: Any) -> str:
    """Pick the first populated source or service URL."""

    for candidate in candidates:
        value = clean(candidate)
        if value:
            return value
    raise ValueError("A curated record is missing an official URL")


def record_from_useful(row: pd.Series) -> dict[str, str]:
    """Convert a content-verified McGill useful-service row."""

    cat_id = category_id(clean(row["category"]))
    return {
        "record_id": clean(row["service_id"]),
        "service_name": clean(row["service_name"]),
        "category_id": cat_id,
        "category_label": TAXONOMY[cat_id],
        "student_need": clean(row["service_description"]) or f"Support related to {TAXONOMY[cat_id]}.",
        "intended_users": clean(row["intended_users"])
        or "McGill students who need this official service.",
        "access_method": clean(row["contact_or_access_methods"]) or clean(row["delivery_context"]),
        "recommended_next_step": clean(row["recommended_next_step"])
        or "Review the official source page for the next step.",
        "limitations": clean(row["limitation"]) or LIMITATIONS[cat_id],
        "official_source_url": official_url(row.get("next_step_url"), row.get("source_url")),
        "source_name": clean(row["service_name"]),
        "source_publisher": "McGill University",
        "source_license_or_terms": source_terms("McGill University"),
        "source_retrieved_at": normalize_timestamp(row.get("last_verified_date")),
        "source_record_id": clean(row["service_id"]),
        "last_verified_date": clean(row["last_verified_date"]) or LAST_VERIFIED_DATE,
        "review_status": CURATED_STATUS,
    }


def record_from_candidate(row: pd.Series) -> dict[str, str]:
    """Convert a selected source-candidate row into the production schema."""

    publisher = clean(row["organization"])
    cat_id = category_id(clean(row["category"]))
    service_name = clean(row["service_name"])
    return {
        "record_id": f"candidate-{clean(row['record_id'])}",
        "service_name": service_name,
        "category_id": cat_id,
        "category_label": TAXONOMY[cat_id],
        "student_need": f"{TAXONOMY[cat_id]}: {service_name}.",
        "intended_users": intended_users_for(publisher, cat_id),
        "access_method": clean(row.get("section")) or clean(row.get("source_page_title")),
        "recommended_next_step": f"Review the official {publisher} source page for {service_name}.",
        "limitations": LIMITATIONS[cat_id],
        "official_source_url": official_url(row.get("service_url"), row.get("source_url")),
        "source_name": clean(row["source_page_title"]) or service_name,
        "source_publisher": publisher,
        "source_license_or_terms": source_terms(publisher),
        "source_retrieved_at": normalize_timestamp(row.get("retrieved_at")),
        "source_record_id": clean(row["record_id"]),
        "last_verified_date": LAST_VERIFIED_DATE,
        "review_status": CURATED_STATUS,
    }


def record_from_guidance(row: pd.Series) -> dict[str, str]:
    """Convert a selected Quebec guidance row into the production schema."""

    publisher = "Gouvernement du Québec"
    cat_id = category_id(clean(row["category"]))
    service_name = clean(row["action_title"])
    return {
        "record_id": f"guidance-{clean(row['record_id'])}",
        "service_name": service_name,
        "category_id": cat_id,
        "category_label": TAXONOMY[cat_id],
        "student_need": f"{TAXONOMY[cat_id]}: {service_name}.",
        "intended_users": "Newcomer students in Quebec who need official settlement guidance.",
        "access_method": clean(row.get("section")) or clean(row.get("source_page_title")),
        "recommended_next_step": f"Review the official Quebec guidance for {service_name}.",
        "limitations": LIMITATIONS[cat_id],
        "official_source_url": official_url(
            row.get("linked_resource_url"),
            row.get("source_page_url"),
        ),
        "source_name": clean(row["source_page_title"]) or service_name,
        "source_publisher": publisher,
        "source_license_or_terms": source_terms(publisher),
        "source_retrieved_at": normalize_timestamp(row.get("retrieved_at")),
        "source_record_id": clean(row["record_id"]),
        "last_verified_date": LAST_VERIFIED_DATE,
        "review_status": CURATED_STATUS,
    }


def intended_users_for(publisher: str, cat_id: str) -> str:
    """Return safe audience wording by source group."""

    if publisher == "McGill University":
        return "McGill newcomer, international, exchange, and current students as applicable."
    if publisher == "Canada Revenue Agency":
        return "Students and newcomer students who need official federal tax information."
    if publisher == "Gouvernement du Québec":
        return "Newcomer students in Quebec who need official public healthcare access information."
    return f"Newcomer students who need {TAXONOMY[cat_id].lower()}."


def build_records() -> list[dict[str, str]]:
    """Build the 40-record curated directory from selected evidence rows."""

    useful = pd.read_csv(DATASETS / "mcgill_useful_service_records.csv")
    proposal = pd.read_csv(DATASETS / "navigator_proposal_samples.csv")
    candidates = pd.read_csv(DATASETS / "navigator_service_candidates.csv")
    guidance = pd.read_csv(DATASETS / "quebec_guidance_catalogue.csv")

    records: list[dict[str, str]] = [record_from_useful(row) for _, row in useful.iterrows()]
    proposal = proposal[~proposal["record_id"].isin(EXCLUDED_PROPOSAL_RECORD_IDS)]
    records.extend(record_from_candidate(row) for _, row in proposal.iterrows())

    selected_external = candidates[
        candidates["record_id"].isin(SELECTED_CRA_RECORD_IDS | SELECTED_QUEBEC_HEALTH_RECORD_IDS)
    ].copy()
    selected_external = selected_external.sort_values(["source_id", "service_name"])
    records.extend(record_from_candidate(row) for _, row in selected_external.iterrows())

    selected_guidance = guidance[
        guidance["record_id"].isin(SELECTED_QUEBEC_HOUSING_RECORD_IDS)
    ].copy()
    selected_guidance = selected_guidance.sort_values(["category", "action_title"])
    records.extend(record_from_guidance(row) for _, row in selected_guidance.iterrows())

    records = sorted(records, key=lambda record: record["record_id"])
    validate_record_count(records)
    return records


def validate_record_count(records: list[dict[str, str]]) -> None:
    """Fail fast if the generated milestone package no longer meets Issue #1 targets."""

    categories = {record["category_id"] for record in records}
    mcgill_count = sum(record["source_publisher"] == "McGill University" for record in records)
    healthcare_wellness_count = sum(
        record["category_id"] in {"health_care", "mental_health"} for record in records
    )

    if len(records) < 40:
        raise ValueError(f"Expected at least 40 records, got {len(records)}")
    if len(categories) < 8:
        raise ValueError(f"Expected at least 8 categories, got {len(categories)}")
    if mcgill_count < 20:
        raise ValueError(f"Expected at least 20 McGill records, got {mcgill_count}")
    if healthcare_wellness_count < 10:
        raise ValueError(
            "Expected at least 10 healthcare/wellness records, "
            f"got {healthcare_wellness_count}"
        )


def write_outputs(records: list[dict[str, str]]) -> None:
    """Write CSV, JSON, and the PR1 quality summary."""

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)

    OUTPUT_JSON.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    QUALITY_REPORT.write_text(render_quality_report(records), encoding="utf-8")


def render_quality_report(records: list[dict[str, str]]) -> str:
    """Render a concise progress-report-ready quality summary."""

    category_counts = Counter(record["category_id"] for record in records)
    publisher_counts = Counter(record["source_publisher"] for record in records)
    mcgill_count = publisher_counts["McGill University"]
    healthcare_wellness_count = sum(
        count
        for category, count in category_counts.items()
        if category in {"health_care", "mental_health"}
    )

    category_table = "\n".join(
        f"| `{category}` | {TAXONOMY[category]} | {count} |"
        for category, count in sorted(category_counts.items())
    )
    publisher_table = "\n".join(
        f"| {publisher} | {count} |" for publisher, count in sorted(publisher_counts.items())
    )

    return f"""# Curated Service Directory Quality Report

Generated: `{LAST_VERIFIED_DATE}`

## Milestone Summary

- Curated service records: **{len(records)}**
- Locked taxonomy categories represented: **{len(category_counts)}**
- McGill records: **{mcgill_count}**
- Healthcare or wellness records: **{healthcare_wellness_count}**
- Review status used for milestone records: `{CURATED_STATUS}`

## Category Coverage

| Category ID | Category label | Records |
| --- | --- | ---: |
{category_table}

## Source Publisher Coverage

| Source publisher | Records |
| --- | ---: |
{publisher_table}

## Validation Coverage

The curated directory is built in the production `ServiceRecord` shape and is checked for:

- required field completeness;
- duplicate `record_id` values;
- URL syntax for official source links and source terms;
- category consistency against the locked taxonomy;
- source provenance fields;
- `last_verified_date` presence;
- ODHF source/license provenance if ODHF-derived records are later surfaced.

Run validation with:

```bash
uv run python scripts/data/validate_curated_service_records.py
```

## Remaining June 21 Gaps

- Muhammad's data package has no validation-blocking gaps.
- Team workflow still needs commit/push, pull-request review, and Issue #1 checklist updates.
- Mustafa should review the field contract in `docs/workflow/service-record-schema.md` before
  finalizing intake/result examples.
- Abdelaziz should use this report and the validation command output as Progress Report 1
  evidence.

## Known Limitations

- Broad scraped candidate files remain discovery evidence; only records in
  `data/datasets/curated_service_records.csv` should power recommendations.
- Candidate-derived records use conservative next-step wording and must not be treated as
  eligibility, medical, immigration, tax, or financial advice.
- This June 21 milestone does not implement production matching logic; it prepares the
  directory and schema contract required for Issue 4.
"""


def main() -> None:
    """Build all June 21 curated-directory artifacts."""

    records = build_records()
    write_outputs(records)
    print(f"Wrote {len(records)} records to {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote JSON mirror to {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Wrote quality report to {QUALITY_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
