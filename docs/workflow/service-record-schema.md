# Service Record Schema

This document defines the June 21 production-format service directory for McGill Care Compass.
Only records in `data/datasets/curated_service_records.csv` should power recommendations.
Broad scraped candidates remain evidence inputs until curated into this schema.

## Required Fields

| Field | Purpose |
| --- | --- |
| `record_id` | Stable unique identifier for the curated record. |
| `service_name` | User-facing service or resource name. |
| `category_id` | Locked taxonomy ID used by intake, matching, UI, and evaluation. |
| `category_label` | Human-readable category label matching the locked taxonomy. |
| `student_need` | Plain-language need or scenario this record can support. |
| `intended_users` | Audience or student group the official source appears to address. |
| `access_method` | How the user can start, contact, book, or navigate the service. |
| `recommended_next_step` | Conservative next step grounded in the official source. |
| `limitations` | Safety, eligibility, freshness, or scope limitation wording. |
| `official_source_url` | Official URL shown to the user. |
| `source_name` | Source page, dataset, or service page name. |
| `source_publisher` | Organization publishing the source. |
| `source_license_or_terms` | Source terms, license, or acceptable-use reference. |
| `source_retrieved_at` | Date or timestamp retained from source evidence. |
| `source_record_id` | Original source-evidence identifier where available. |
| `last_verified_date` | Date the project last checked or curated the record. |
| `review_status` | Current curation state for the milestone dataset. |

## UI and Matcher Contract

Mustafa's intake, results UI, and Issue 4 matcher can rely on every curated record having:

- a stable `record_id` for tracking and display keys;
- `category_id` and `category_label` for intake/category matching;
- `service_name`, `student_need`, and `intended_users` for result selection and display;
- `access_method` and `recommended_next_step` for next-step wording;
- `limitations` for high-risk, eligibility, freshness, or safety wording;
- `official_source_url`, `source_publisher`, and `last_verified_date` for source display.

The June 21 directory does not guarantee live service availability, individual eligibility,
medical triage, immigration/legal interpretation, tax advice, or production scoring rules.
Those responsibilities remain in the guardrails, matching, and evaluation issues.

## Locked Taxonomy

| Category ID | Category label |
| --- | --- |
| `health_care` | Healthcare access |
| `mental_health` | Mental health and wellbeing |
| `insurance` | Health insurance and coverage |
| `immigration_status` | Immigration and legal status |
| `housing` | Housing and basic needs |
| `academics` | Academic and advising support |
| `finances` | Financial aid and affordability |
| `work_career` | Work and career support |
| `tax` | Tax filing and residency information |
| `documents_admin` | Campus documents and administration |
| `language_integration` | Language and integration |
| `safety_urgent` | Urgent or safety-related help |

## Source Authority Rules

- Prefer official McGill sources for McGill-owned student services.
- Prefer official Quebec, federal, RAMQ, or healthcare-system sources for government,
  healthcare, tax, insurance, and eligibility-adjacent topics.
- Use community or external records only when they are trusted, source-linked, and scoped with
  limitations.
- Do not treat broad scraped candidates as approved recommendation records until they are
  normalized into `curated_service_records.csv`.
- ODHF-derived facility records must include source name, publisher, source URL or terms,
  retrieval date, original record ID where available, and last-verified date.

## Reproducible Commands

Build the curated directory and quality report:

```bash
uv run python scripts/data/build_curated_service_records.py
```

Validate the June 21 acceptance checks:

```bash
uv run python scripts/data/validate_curated_service_records.py
```
