# RAG Data Pipeline v1

Muhammad's v1 data layer uses a reusable local RAG pipeline as the active
retrieval source. The previous static service-record workflow has been removed.

## Data Flow

```text
seed URLs
  -> Bronze raw HTML snapshots
  -> Silver clean text and link/page manifests
  -> Silver header-aware chunks
  -> Silver questionnaire metadata tags
  -> Silver local embeddings
  -> Silver Chroma vector store
```

The pipeline is source-grounded and local-first. It uses official seed URLs,
the locked taxonomy, and questionnaire metadata IDs shared with Mustafa's UX
work.

The crawler records every discovered link, but only queues a bounded number of
in-scope links from each page. The default queue limit is 10 links per page, and
links are ranked before queueing so action-oriented student service links are
preferred over news, staff, calendar, login, and other lower-value navigation
links. This keeps the depth-3 crawl from being consumed by one large
navigation-heavy source. Each seed also carries source ownership, terms,
allowlist, max-depth, and max-pages guardrails in
`data/source-inputs/rag_seed_urls.csv`.

## Persistent Outputs

| Output | Purpose |
| --- | --- |
| `data/source-inputs/rag_seed_urls.csv` | Official source URLs, taxonomy, and crawl boundaries. |
| `data/source-inputs/questionnaire_metadata_map.yml` | Stable questionnaire IDs and tagging keywords. |
| `data/bronze/raw/rag_pages/` | Bronze exact fetched HTML, stored locally and ignored by git. |
| `data/silver/processed/rag_pages/` | Silver clean boilerplate-removed text, stored locally and ignored by git. |
| `data/silver/rag/rag_metadata.sqlite` | Silver durable page/link/chunk metadata, stored locally and ignored by git. |
| `data/silver/datasets/rag_pages.csv` | Silver reviewable page manifest and drift state. |
| `data/silver/datasets/rag_links.csv` | Silver reviewable sublink graph and crawl decisions. |
| `data/silver/datasets/rag_chunks.csv` | Silver reviewable chunk table used to rebuild vectors. |
| `data/silver/vector_store/chroma/` | Silver local Chroma vector index, rebuildable from chunks and ignored by git. |
| `data/silver/reports/rag_pipeline_report.md` | Silver progress-report summary of the latest run. |
| `data/silver/reports/rag_run_manifest.json` | Machine-readable run manifest tying artifacts to the pipeline version and config hashes. |
| `data/gold/` | Reserved for future reviewed, release-ready data; empty in the current version. |

Bronze is unprocessed. Silver is processed/generated but not manually reviewed as final
recommendation data. Gold requires explicit team review before any dataset is added.

The latest v1 run contains 500 pages, 22,727 discovered links, 4,228 chunks,
and 11 categories. Exact run details live in
`data/silver/reports/rag_run_manifest.json`.

## Source and Terms Contract

The pipeline persists source metadata on both pages and chunks so the future
agent can rank and cite retrieved information without joining extra tables.

Important fields:

| Field | Purpose |
| --- | --- |
| `seed_url_id` | Stable ID for the source URL that introduced the page. |
| `domain` | Allowlist/reporting domain. |
| `source_group` | Normalized source group such as `canada`, `quebec`, or `mcgill`. |
| `source_owner` | Office, agency, service, or organization that owns the source. |
| `authority_level` | Source-authority label from the seed table. |
| `terms_url` | Copyright, license, or terms page for the source. |
| `licence_or_terms` | Current MVP value: `allows_non_commercial_or_link_and_paraphrase`. |
| `source_priority_rank` | Lower-is-better source priority used for reranking. |
| `freshness_score` | Higher-is-fresher score from source modified date or retrieval time. |

The reusable ranking helper is in `src/mcgill_care_compass/rag_ranking.py`.
Retrieval reranking follows this project-specific source preference order:
Canada, Quebec, official healthcare systems, McGill, then other approved
sources. Within the same source tier, fresher source dates are preferred.

Seed-level crawl guardrails include:

| Field | Purpose |
| --- | --- |
| `allowed_to_crawl` | Whether sublinks from the seed may be followed. |
| `max_depth` | Per-seed depth limit, capped again by the CLI max-depth. |
| `max_pages_from_seed` | Per-seed page cap, capped again by the CLI max-pages. |
| `crawl_notes` | Manual source limits or review notes. |

Link-level crawl guardrails include:

| Field | Purpose |
| --- | --- |
| `link_priority_score` | Deterministic score used to choose which in-scope links are queued first. |
| `link_priority_reasons` | Audit trail for the score, such as questionnaire, service-term, category, or deprioritized matches. |
| `crawl_decision` | Whether the discovered link was queued or recorded only. |
| `skip_reason` | Reason a link was not crawled, such as depth limit, duplicate URL, file, external domain, or per-page link limit. |

## Version Governance

Every generated page, link, and chunk row carries the same run metadata:

- `pipeline_version`
- `pipeline_run_id`
- `artifact_schema_version`
- `generated_at`
- `questionnaire_metadata_version`
- `seed_config_hash`
- `questionnaire_config_hash`
- `crawl_config_hash`
- `chunking_config_version`
- `link_priority_config_version`
- `embedding_model`

The same fields are written into `data/silver/reports/rag_run_manifest.json`.
The manifest also records row counts and SHA-256 hashes for the page, link,
chunk, SQLite, and report artifacts. This means a reviewer can verify exactly
which pipeline/config/model generated a Silver artifact and detect stale or
mixed-run files.

Current v1 values:

| Field | Value |
| --- | --- |
| `pipeline_version` | `1.0.0` |
| `artifact_schema_version` | `1` |
| `questionnaire_metadata_version` | `2` |
| `chunking_config_version` | `1` |
| `link_priority_config_version` | `1` |
| `embedding_model` | `sentence-transformers/all-MiniLM-L6-v2` |

## Chunking Contract

Chunks are header-aware. The parser keeps `h1`/`h2`/`h3`/useful `h4`
headings, attaches content to the nearest section, stores the heading as
metadata, and prepends the heading path to `embedding_text`.

Example:

```text
heading_path: International Health Insurance > Costs
chunk_text: If you consult a doctor, you are covered at 100%...
embedding_text: International Health Insurance > Costs: If you consult a doctor...
```

This keeps retrieval aligned with student questions such as "what does it
cost?", "am I eligible?", and "how do I apply?"

## Questionnaire Contract

Mustafa's questionnaire and Muhammad's chunk metadata should use the stable IDs
in `questionnaire_metadata_map.yml`. UI labels can change without breaking
retrieval. The shared chunk-aligned fields are:

- `category_id`
- `need_type`
- `student_type`
- `jurisdiction`
- `language`
- derived `risk_level`

`need_type` is not stored as one standalone chunk column. It maps to `info_type_tags`
and the boolean fields `has_contact_info`, `has_required_docs`, `has_eligibility`,
`has_costs_coverage`, `has_location`, `has_deadlines`, `has_booking_steps`, and
`has_emergency_info`. Mustafa's `general_navigation` need type uses category and
semantic search without requiring a boolean tag.

If Mustafa adds a new option, update the YAML and rerun:

```bash
uv run python scripts/data/build_rag_corpus.py --metadata-only
```

This refreshes chunk metadata without refetching websites.

## Drift Monitoring

Each page stores raw HTML, clean text, link, and section hashes. On rerun:

- same clean-text hash -> `unchanged`
- new URL -> `new`
- changed clean-text hash -> `changed`
- fetch error -> `fetch_failed`

Changed pages are re-parsed, re-chunked, and re-vectorized. Unchanged pages can
be skipped in later optimizations; the current MVP rebuilds the local Chroma
index from the active chunk table for reliability.

## Commands

Build or refresh the full local corpus:

```bash
uv run python scripts/data/build_rag_corpus.py
```

Validate the corpus:

```bash
uv run python scripts/data/validate_rag_corpus.py
```

Run a retrieval smoke query:

```bash
uv run python scripts/data/query_rag_corpus.py \
  --query "How do I know what health insurance covers?" \
  --category-id insurance \
  --need-type costs_coverage
```
