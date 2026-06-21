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

## Actionable Enrichment (v1)

The curated directory above is the stable base. A second, *enriched* dataset adds
source-grounded "useful info" so recommendations can give a concrete next step
instead of only linking out. It is produced by a re-runnable pipeline.

- Enriched dataset: `data/datasets/actionable_service_records.csv` (+ `.json` mirror)
- Pipeline report: `data/reports/actionable_service_pipeline_report.md`

It keeps every base field and adds:

| Field | Purpose |
| --- | --- |
| `actionable_summary` | Plain-language description of the service, from the official page. |
| `actionable_next_step` | Concrete next step composed from extracted specifics (never "visit the website"). |
| `eligibility_or_requirements` | Eligibility / requirement snippets quoted from the page. |
| `access_steps` | How to access, book, or apply, quoted from the page. |
| `costs_or_coverage` | Cost, fee, or coverage details, where stated. |
| `contact_or_location` | Phone, email, or contact links extracted from the page. |
| `source_evidence_excerpt` | The supporting snippet the fields are grounded in. |
| `extraction_status` | `enriched`, `partial`, `fetch_failed`, or `not_targeted`. |
| `content_last_checked_at` | UTC timestamp of the last fetch. |
| `source_content_hash` | Hash of page content for change detection on re-runs. |

`extraction_status` values:

- `enriched` — useful summary + concrete steps + at least one of contact / eligibility / cost.
- `partial` — reachable but thin (often a generic landing page); summary/contact only.
- `fetch_failed` — the page could not be fetched.
- `not_targeted` — deferred for v1 (currently the CRA / tax records: canada.ca blocks automated fetching).

Contract for the recommendation / UX layer (Issue 5): prefer `actionable_next_step`,
`access_steps`, `eligibility_or_requirements`, `costs_or_coverage`, and
`contact_or_location`, and always show `official_source_url`, `last_verified_date`,
and `limitations`. Treat these as source-grounded facts, not advice — final wording is
composed by the agent / Responses layer. For records that are not `enriched`, fall
back to the base curated next step.

Reusable refresh (re-fetches, re-extracts, and flags pages that changed):

```bash
uv run python scripts/data/build_actionable_service_records.py
uv run python scripts/data/validate_actionable_service_records.py
```

> v1 note: extraction is deterministic and source-grounded (no LLM). Output structure
> is stable across runs; `content_last_checked_at` changes each run by design.
