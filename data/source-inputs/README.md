# Source Inputs

This folder contains configuration for the v1 RAG pipeline. It is not a
Bronze/Silver/Gold data layer because these files are not crawled outputs; they
control how the pipeline runs.

## Files

| File | Purpose |
| --- | --- |
| [`rag_seed_urls.csv`](rag_seed_urls.csv) | Official seed URLs, source ownership, source authority, allowlists, per-seed crawl limits, taxonomy, source terms, and default user-context metadata. |
| [`questionnaire_metadata_map.yml`](questionnaire_metadata_map.yml) | Stable questionnaire IDs, category IDs, need-type IDs, keyword rules, and fields shared with Mustafa's intake flow. |

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

## Version Governance

`risk_level` is kept for v1 compatibility, but it should be read as topic sensitivity, not actual chunk-level danger. Future work may rename it to `topic_sensitivity` or let the app derive sensitive-topic behavior directly from the taxonomy.

Both source-input files are hashed into
[`data/silver/reports/rag_run_manifest.json`](../silver/reports/rag_run_manifest.json) and stamped onto every generated
page, link, and chunk row. If either file changes, the next generated Silver
artifacts carry new config hashes.
