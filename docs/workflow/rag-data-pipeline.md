# RAG Data Pipeline v1

Muhammad's v1 data layer uses a local RAG pipeline as the active retrieval source. It crawls approved official pages, creates reviewable Silver artifacts, and rebuilds local runtime indexes from committed CSVs.

## Lifecycle

```text
seed configuration
  -> crawl approved official pages
  -> store local Bronze raw HTML
  -> clean text and extract links
  -> create Silver page/link manifests
  -> create header-aware Silver chunks
  -> apply questionnaire metadata tags
  -> rebuild local Chroma vectors
  -> write reports and run manifest
  -> validate corpus before use
```

Bronze is unprocessed and local. Silver is processed, queryable, and reviewable, but not approved as final recommendation data. Gold is reserved for future reviewed, release-ready outputs and is empty in v1.

## Artifact Flow

| Artifact | Role | Git status |
| --- | --- | --- |
| [`data/source-inputs/rag_seed_urls.csv`](../../data/source-inputs/rag_seed_urls.csv) | Official seed URLs, source ownership, source authority, allowlists, taxonomy, and crawl limits. | Tracked |
| [`data/source-inputs/questionnaire_metadata_map.yml`](../../data/source-inputs/questionnaire_metadata_map.yml) | Stable questionnaire IDs, category IDs, need-type IDs, and keyword/tag rules. | Tracked |
| [`data/bronze/raw/rag_pages/`](../../data/README.md) | Exact fetched HTML snapshots for debugging and reruns. | Ignored |
| [`data/silver/processed/rag_pages/`](../../data/README.md) | Cleaned text after boilerplate removal. | Ignored |
| [`data/silver/datasets/rag_pages.csv`](../../data/silver/datasets/rag_pages.csv) | Page manifest, source metadata, drift state, and run stamp. | Tracked |
| [`data/silver/datasets/rag_links.csv`](../../data/silver/datasets/rag_links.csv) | Discovered-link graph, priority scores, crawl decisions, and skip reasons. | Tracked |
| [`data/silver/datasets/rag_chunks.csv`](../../data/silver/datasets/rag_chunks.csv) | Header-aware retrieval chunks, metadata tags, provenance, and vector IDs. | Tracked |
| [`data/silver/rag/rag_metadata.sqlite`](../../data/README.md) | Local SQLite copy of page/link/chunk metadata. | Ignored |
| [`data/silver/vector_store/chroma/`](../../data/README.md) | Local Chroma vector index rebuilt from [`rag_chunks.csv`](../../data/silver/datasets/rag_chunks.csv). | Ignored |
| [`data/silver/reports/rag_pipeline_report.md`](../../data/silver/reports/rag_pipeline_report.md) | Human-readable run summary. | Tracked |
| [`data/silver/reports/rag_corpus_quality_report.md`](../../data/silver/reports/rag_corpus_quality_report.md) | Chunk-quality warnings and cleanup guidance. | Tracked |
| [`data/silver/reports/rag_run_manifest.json`](../../data/silver/reports/rag_run_manifest.json) | Machine-readable run metadata, row counts, config hashes, and artifact hashes. | Tracked |
| [`data/gold/`](../../data/gold/) | Future reviewed release-ready data. | README only in v1 |

## Current Run Snapshot

The latest v1 run contains 500 pages, 22,727 discovered links, 4,228 chunks, and 11 categories. Exact counts, hashes, model/version values, and artifact paths live in [`data/silver/reports/rag_run_manifest.json`](../../data/silver/reports/rag_run_manifest.json).

## Commands

Build or refresh the full local corpus:

```bash
uv run python scripts/data/build_rag_corpus.py
```

Refresh questionnaire metadata without refetching websites:

```bash
uv run python scripts/data/build_rag_corpus.py --metadata-only
```

Force rechunking from existing cleaned pages:

```bash
uv run python scripts/data/build_rag_corpus.py --force-rechunk
```

Validate the corpus and local runtime artifacts:

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

## Operating Rules

- Rebuild Chroma from [`data/silver/datasets/rag_chunks.csv`](../../data/silver/datasets/rag_chunks.csv); do not commit the vector store.
- Treat `risk_level` as legacy topic-sensitivity metadata, not actual chunk danger.
- If taxonomy, questionnaire IDs, source authority, or metadata rules change, update the source-input files and rerun the pipeline.
- Use Silver chunks for prototype retrieval only with source links, limitation wording, and evidence checks.
- Promote data to Gold only after explicit review.
