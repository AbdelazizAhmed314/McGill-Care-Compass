# Source Inputs

This folder contains configuration for the v1 RAG pipeline. It is not a
Bronze/Silver/Gold data layer because these files are not crawled outputs; they
control how the pipeline runs.

## Files

| File | Purpose |
| --- | --- |
| [`rag_seed_urls.csv`](rag_seed_urls.csv) | Official seed URLs, source ownership, source authority, allowlists, per-seed crawl limits, taxonomy, source terms, and default user-context metadata. |
| [`questionnaire_metadata_map.yml`](questionnaire_metadata_map.yml) | Stable questionnaire IDs, category IDs, need-type IDs, keyword rules, and fields shared with Mustafa's intake flow. |
| [`rag_failed_source_dispositions.csv`](rag_failed_source_dispositions.csv) | Explicit reviews that may downgrade a known zero-chunk fetch failure from an error to a warning. |
| [`rag_required_source_urls.csv`](rag_required_source_urls.csv) | Additional service-critical URLs that can never be downgraded when a fetch fails. Seed URLs are already non-waivable and do not need to be repeated here. |

## Seed Contract

Each seed row defines:

- stable `seed_url_id`
- official source URL and domain
- `source_group`, `source_owner`, `source_publisher`, and `authority_level`
- `allowed_domains` and `allowed_path_prefixes`
- `allowed_to_crawl`, `max_depth`, and `max_pages_from_seed`
- `category_id` and `category_label`
- `student_type`, `jurisdiction`, `language`, and legacy `risk_level` topic-sensitivity metadata
- `terms_url` and `licence_or_terms`

The crawler inherits this metadata onto pages and chunks.

## Questionnaire Contract

The questionnaire map defines the stable IDs used by both the UI and the RAG
pipeline. Display wording can change without changing the data pipeline as long
as stable IDs remain the same.

Changing display wording usually requires:

```bash
uv run python scripts/data/build_rag_corpus.py --metadata-only
```

Changing seed URLs, allowlists, source ownership, crawl limits, or source terms
requires a full rebuild:

```bash
uv run python scripts/data/build_rag_corpus.py --force-rechunk
```

## Failed-Source Disposition Contract

Failed page fetches block the maintenance error gate by default. A disposition
is valid only when it uses `reviewed_nonblocking` and includes:

- the exact canonical URL
- a concrete reason the page is not required for current service/category coverage
- an ISO review date
- an issue or review reference
- the exact governed `pipeline_run_id` reviewed
- an official `replacement_url` in the same category with active chunks from that
  pipeline run

A seed page can never receive a nonblocking disposition. A non-seed failure
listed in `rag_required_source_urls.csv`, or one without machine-verifiable
replacement coverage, also remains blocking. Add a URL to that file when a
non-seed page is service-critical and no replacement is acceptable. The review
date cannot be in the future and expires after 30 calendar days. A disposition
never exempts a failed page that still supplies active chunks. A new corpus run
invalidates old dispositions, requiring reviewers to reassess the current fetch
result and coverage. Remove obsolete rows when a source is restored, replaced,
or becomes required.

## Version Governance

`risk_level` is kept for v1 compatibility, but it should be read as topic sensitivity, not actual chunk-level danger. Future work may rename it to `topic_sensitivity` or let the app derive sensitive-topic behavior directly from the taxonomy.

The seed and questionnaire configuration files are hashed into
[`data/silver/reports/rag_run_manifest.json`](../silver/reports/rag_run_manifest.json) and stamped onto every generated
page, link, and chunk row. If either file changes, the next generated Silver
artifacts carry new config hashes.

Failed-source dispositions and the required-source list are operational review
policy, not corpus-generation inputs, so they are version controlled but are
not included in the corpus configuration hashes.
