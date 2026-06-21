# Actionable Service Pipeline Report (v1)

Generated: `2026-06-21T01:44:54+00:00`

## What this run did

Fetched the official source page for each targeted record in
`data/datasets/curated_service_records.csv` and extracted source-grounded useful
info (summary, eligibility, concrete steps, cost/coverage, contact) into
`data/datasets/actionable_service_records.csv`. No LLM is used; extraction is
deterministic and quoted from the official pages.

## Status summary

- enriched: **31**
- partial: **8**
- fetch_failed: **0**
- not_targeted: **5** (deferred: canada.ca / CRA tax pages block automated fetching)

Total records: **44**

## Enriched coverage in priority categories

| Category | Enriched records |
| --- | ---: |
| `health_care` | 6 |
| `insurance` | 3 |
| `immigration_status` | 2 |
| `housing` | 4 |

## Fetch failures

- none

## Change detection (vs. previous run)

- none (first run or no changes detected)

## Known gaps / next cycle

- CRA / tax records are deferred: canada.ca blocks automated fetching. Next cycle
  options: official API, a headless-browser fetch, or curated manual extraction.
- `partial` records were reachable but yielded thin structured content (often
  generic landing pages); they can be deep-linked or manually curated next.
- The user-facing recommendation wording is produced later by the agent/Responses
  layer from these fields; this pipeline only produces the structured data.

## Reproduce / refresh

```bash
uv run python scripts/data/build_actionable_service_records.py
uv run python scripts/data/validate_actionable_service_records.py
```
