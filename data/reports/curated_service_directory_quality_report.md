# Curated Service Directory Quality Report

Generated: `2026-06-19`

## Milestone Summary

- Curated service records: **44**
- Locked taxonomy categories represented: **11**
- McGill records: **31**
- Healthcare or wellness records: **13**
- Review status used for milestone records: `curated_for_directory_milestone`

## Category Coverage

| Category ID | Category label | Records |
| --- | --- | ---: |
| `academics` | Academic and advising support | 2 |
| `documents_admin` | Campus documents and administration | 2 |
| `finances` | Financial aid and affordability | 5 |
| `health_care` | Healthcare access | 8 |
| `housing` | Housing and basic needs | 4 |
| `immigration_status` | Immigration and legal status | 2 |
| `insurance` | Health insurance and coverage | 3 |
| `language_integration` | Language and integration | 2 |
| `mental_health` | Mental health and wellbeing | 5 |
| `tax` | Tax filing and residency information | 5 |
| `work_career` | Work and career support | 6 |

## Source Publisher Coverage

| Source publisher | Records |
| --- | ---: |
| Canada Revenue Agency | 5 |
| Gouvernement du Québec | 8 |
| McGill University | 31 |

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
